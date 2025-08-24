from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from datetime import datetime

from models.cleanup import CleanupManager, CleanupStatus
from models.rewards import RewardsManager
from config import Config

# Create blueprint
cleanup = Blueprint('cleanup', __name__)

# Initialize managers
cleanup_manager = CleanupManager(
    Config.BASE_DIR / "static" / "data" / "cleanups.json",
    Config.BASE_DIR / "static" / "data" / "teams.json"
)

rewards_manager = RewardsManager(
    Config.BASE_DIR / "static" / "data" / "rewards.json",
    Config.BASE_DIR / "static" / "data" / "badges.json"
)

@cleanup.route("/cleanup-dashboard")
def cleanup_dashboard():
    """Display the main cleanup dashboard."""
    stats = cleanup_manager.get_cleanup_stats()
    cleanups = cleanup_manager.load_cleanups()
    teams = cleanup_manager.load_teams()
    
    # Get user info from session
    user_email = session.get("email") if "user_id" in session else None
    
    return render_template(
        "cleanup/dashboard.html",
        stats=stats,
        cleanups=cleanups,
        teams=teams,
        user_email=user_email
    )

@cleanup.route("/cleanup-reports")
def cleanup_reports():
    """Display all cleanup reports with filtering."""
    status_filter = request.args.get("status", "all")
    cleanups = cleanup_manager.load_cleanups()
    teams = cleanup_manager.load_teams()
    
    # Filter by status if specified
    if status_filter != "all":
        cleanups = [c for c in cleanups if c["status"] == status_filter]
    
    # Get user info from session
    user_email = session.get("email") if "user_id" in session else None
    
    return render_template(
        "cleanup/reports.html",
        cleanups=cleanups,
        teams=teams,
        current_filter=status_filter,
        statuses=CleanupStatus.__dict__,
        user_email=user_email
    )

@cleanup.route("/create-team", methods=["GET", "POST"])
def create_team():
    """Create a new cleanup team."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        leader_email = request.form.get("leader_email", "").strip()
        members = request.form.getlist("members[]")  # Get array of members
        
        if not name or not leader_email:
            flash("Team name and leader email are required", "error")
            return redirect(url_for("cleanup.create_team"))
        
        # Process members array and filter out empty values
        member_list = [email.strip() for email in members if email.strip()]
        
        # Ensure leader is included in members list
        if leader_email not in member_list:
            member_list.append(leader_email)
        
        # Validate we have at least 2 members (leader + 1 member)
        if len(member_list) < 2:
            flash("Team must have at least 2 members (including leader)", "error")
            return redirect(url_for("cleanup.create_team"))
        
        try:
            team_id = cleanup_manager.create_team(name, leader_email, member_list)
            flash(f"Team '{name}' created successfully with {len(member_list)} members!", "success")
            return redirect(url_for("cleanup.create_team", success="true"))
        except Exception as e:
            flash(f"Error creating team: {str(e)}", "error")
    
    return render_template("cleanup/create_team.html")

@cleanup.route("/team/<team_id>")
def team_details(team_id):
    """Display team details and current tasks."""
    teams = cleanup_manager.load_teams()
    team = next((t for t in teams if t["team_id"] == team_id), None)
    
    if not team:
        flash("Team not found", "error")
        return redirect(url_for("cleanup.cleanup_dashboard"))
    
    # Get team's current and past tasks
    cleanups = cleanup_manager.load_cleanups()
    team_cleanups = [c for c in cleanups if c.get("assigned_team") == team_id]
    
    # Get user info from session
    user_email = session.get("email") if "user_id" in session else None
    
    return render_template(
        "cleanup/team_details.html",
        team=team,
        cleanups=team_cleanups,
        user_email=user_email
    )

@cleanup.route("/update-status/<report_id>", methods=["POST"])
def update_status(report_id):
    """Update cleanup status."""
    status = request.form.get("status")
    notes = request.form.get("notes", "").strip()
    
    if not status:
        flash("Status is required", "error")
        return redirect(url_for("cleanup.cleanup_reports"))
    
    try:
        success = cleanup_manager.update_cleanup_status(report_id, status, notes)
        if success:
            flash("Status updated successfully!", "success")
        else:
            flash("Error updating status", "error")
    except Exception as e:
        flash(f"Error updating status: {str(e)}", "error")
    
    return redirect(url_for("cleanup.cleanup_reports"))

@cleanup.route("/assign-team/<report_id>", methods=["POST"])
def assign_team(report_id):
    """Manually assign a team to a cleanup task."""
    team_id = request.form.get("team_id")
    
    if not team_id:
        flash("Team selection is required", "error")
        return redirect(url_for("cleanup.cleanup_reports"))
    
    try:
        # Manual assignment logic
        cleanups = cleanup_manager.load_cleanups()
        teams = cleanup_manager.load_teams()
        
        cleanup = next((c for c in cleanups if c["report_id"] == report_id), None)
        team = next((t for t in teams if t["team_id"] == team_id), None)
        
        if not cleanup or not team:
            flash("Report or team not found", "error")
            return redirect(url_for("cleanup.cleanup_reports"))
        
        if team["status"] != "available":
            flash("Selected team is not available", "error")
            return redirect(url_for("cleanup.cleanup_reports"))
        
        # Assign team
        cleanup["assigned_team"] = team_id
        cleanup["assigned_date"] = datetime.now().isoformat()
        cleanup["status"] = CleanupStatus.IN_PROGRESS
        cleanup["updated_at"] = datetime.now().isoformat()
        
        # Update team status
        team["status"] = "busy"
        team["current_task"] = report_id
        team["last_activity"] = datetime.now().isoformat()
        
        cleanup_manager.save_cleanups(cleanups)
        cleanup_manager.save_teams(teams)
        
        flash(f"Team '{team['name']}' assigned successfully!", "success")
        
    except Exception as e:
        flash(f"Error assigning team: {str(e)}", "error")
    
    return redirect(url_for("cleanup.cleanup_reports"))

@cleanup.route("/rewards/<email>")
def user_rewards(email):
    """Display user rewards and achievements."""
    user_stats = rewards_manager.get_user_stats(email)
    
    return render_template(
        "cleanup/rewards.html",
        user_stats=user_stats
    )

@cleanup.route("/api/cleanup-stats")
def api_cleanup_stats():
    """API endpoint for cleanup statistics."""
    stats = cleanup_manager.get_cleanup_stats()
    return jsonify(stats)

@cleanup.route("/api/available-teams")
def api_available_teams():
    """API endpoint for available teams."""
    teams = cleanup_manager.load_teams()
    available_teams = [t for t in teams if t["status"] == "available"]
    return jsonify(available_teams)



@cleanup.route("/team-tasks")
def team_tasks():
    """Show cleanup tasks for a specific team member."""
    email = request.args.get("email")
    if not email:
        flash("Email parameter required", "error")
        return redirect(url_for("cleanup.cleanup_dashboard"))
    
    team_tasks = cleanup_manager.get_team_cleanup_tasks(email)
    
    return render_template("cleanup/team_tasks.html", email=email, tasks=team_tasks)

@cleanup.route("/verify-cleanup/<report_id>", methods=["GET", "POST"])
def verify_cleanup(report_id):
    """Show cleanup verification form and handle verification submission."""
    try:
        # Get cleanup data
        cleanups = cleanup_manager.load_cleanups()
        teams = cleanup_manager.load_teams()
        
        cleanup = next((c for c in cleanups if c["report_id"] == report_id), None)
        if not cleanup:
            flash("Cleanup report not found", "error")
            return redirect(url_for("cleanup.cleanup_dashboard"))
        
        # Check if team is assigned
        if not cleanup.get("assigned_team"):
            flash("No team assigned to this cleanup", "error")
            return redirect(url_for("cleanup.cleanup_dashboard"))
        
        # Get team data
        team = next((t for t in teams if t["team_id"] == cleanup["assigned_team"]), None)
        if not team:
            flash("Assigned team not found", "error")
            return redirect(url_for("cleanup.cleanup_dashboard"))
        
        # Get user info from session
        user_email = session.get("email") if "user_id" in session else None
        
        if request.method == "GET":
            return render_template(
                "cleanup/verify_cleanup.html",
                cleanup=cleanup,
                team=team,
                user_email=user_email
            )
        
        elif request.method == "POST":
            # Handle verification submission
            email = request.form.get("email", "").strip()
            notes = request.form.get("notes", "").strip()
            verification_photos = request.files.getlist("verification_photos")
            
            # Validate email is team member
            if email not in team["members"]:
                flash("Email must be a member of the assigned cleanup team", "error")
                return redirect(url_for("cleanup.verify_cleanup", report_id=report_id))
            
            # Validate photos
            if not verification_photos or not verification_photos[0].filename:
                flash("At least one verification photo is required", "error")
                return redirect(url_for("cleanup.verify_cleanup", report_id=report_id))
            
            try:
                # Save verification photos
                photo_paths = []
                for photo in verification_photos:
                    if photo and photo.filename:
                        filename = secure_filename(f"verification_{report_id}_{photo.filename}")
                        photo_path = Config.UPLOAD_FOLDER / filename
                        photo.save(photo_path)
                        photo_paths.append(filename)
                
                # Analyze photos with Gemini AI
                from utils.analysis import analyze_cleanup_verification
                analysis_results = []
                
                for photo_path in photo_paths:
                    full_path = Config.UPLOAD_FOLDER / photo_path
                    result = analyze_cleanup_verification(str(full_path))
                    analysis_results.append(result)
                
                # Calculate average cleanup score
                if analysis_results:
                    avg_score = sum(result.get("score", 0) for result in analysis_results) / len(analysis_results)
                    
                    # Determine if cleanup is successful (score < 30 means good cleanup)
                    if avg_score < 30:
                        # Mark as completed
                        cleanup["status"] = CleanupStatus.CLEANED
                        cleanup["completion_date"] = datetime.now().isoformat()
                        cleanup["updated_at"] = datetime.now().isoformat()
                        
                        # Free up the team
                        team["status"] = "available"
                        team["current_task"] = None
                        team["last_activity"] = datetime.now().isoformat()
                        team["total_cleanups"] += 1
                        
                        # Award points to team members
                        team_points = 25  # Base points for completion
                        for member_email in team["members"]:
                            rewards_manager.award_points(member_email, team_points, "cleanup")
                        
                        # Save verification data
                        cleanup["verification_photos"] = photo_paths
                        cleanup["cleanup_notes"] = notes
                        cleanup["verification_analysis"] = analysis_results
                        cleanup["cleanup_score"] = avg_score
                        
                        # Save changes
                        cleanup_manager.save_cleanups(cleanups)
                        cleanup_manager.save_teams(teams)
                        
                        flash(f"🎉 Cleanup verification successful! Area is clean (score: {avg_score:.1f}/100). Team '{team['name']}' has been freed and awarded {team_points} points each!", "success")
                        return redirect(url_for("cleanup.cleanup_dashboard"))
                    else:
                        # Cleanup not sufficient
                        cleanup["verification_photos"] = photo_paths
                        cleanup["cleanup_notes"] = notes
                        cleanup["verification_analysis"] = analysis_results
                        cleanup["cleanup_score"] = avg_score
                        cleanup["updated_at"] = datetime.now().isoformat()
                        
                        # Save changes
                        cleanup_manager.save_cleanups(cleanups)
                        
                        flash(f"⚠️ Cleanup verification shows area still needs work (score: {avg_score:.1f}/100). Please continue cleaning and submit new photos.", "warning")
                        return redirect(url_for("cleanup.verify_cleanup", report_id=report_id))
                
            except Exception as e:
                flash(f"Error processing verification: {str(e)}", "error")
                return redirect(url_for("cleanup.verify_cleanup", report_id=report_id))
    
    except Exception as e:
        flash(f"Error accessing cleanup verification: {str(e)}", "error")
        return redirect(url_for("cleanup.cleanup_dashboard"))

@cleanup.route("/mark-completed/<report_id>", methods=["POST"])
def mark_completed(report_id):
    """Allow team leader to mark cleanup as completed."""
    try:
        # Get cleanup data
        cleanups = cleanup_manager.load_cleanups()
        teams = cleanup_manager.load_teams()
        
        cleanup = next((c for c in cleanups if c["report_id"] == report_id), None)
        if not cleanup:
            flash("Cleanup report not found", "error")
            return redirect(url_for("cleanup.cleanup_dashboard"))
        
        # Check if team is assigned
        if not cleanup.get("assigned_team"):
            flash("No team assigned to this cleanup", "error")
            return redirect(url_for("cleanup.cleanup_dashboard"))
        
        # Get team data
        team = next((t for t in teams if t["team_id"] == cleanup["assigned_team"]), None)
        if not team:
            flash("Assigned team not found", "error")
            return redirect(url_for("cleanup.cleanup_dashboard"))
        
        # Update cleanup status
        cleanup["status"] = CleanupStatus.CLEANED
        cleanup["completion_date"] = datetime.now().isoformat()
        cleanup["updated_at"] = datetime.now().isoformat()
        
        # Free up the team
        team["status"] = "available"
        team["current_task"] = None
        team["last_activity"] = datetime.now().isoformat()
        team["total_cleanups"] += 1
        
        # Award points to team members
        team_points = 25  # Base points for completion
        for member_email in team["members"]:
            rewards_manager.award_points(member_email, team_points, "cleanup")
        
        # Save changes
        cleanup_manager.save_cleanups(cleanups)
        cleanup_manager.save_teams(teams)
        
        flash(f"🎉 Cleanup marked as completed! Team '{team['name']}' has been freed and awarded {team_points} points each!", "success")
        
    except Exception as e:
        flash(f"Error marking cleanup as completed: {str(e)}", "error")
    
    return redirect(url_for("cleanup.cleanup_dashboard"))
