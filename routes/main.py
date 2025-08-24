from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from pathlib import Path

from models.report import Report, ReportManager
from models.cleanup import CleanupManager
from models.rewards import RewardsManager
from utils.analysis import PollutionAnalyzer, LocationUtils
from config import Config

# Create blueprint
main = Blueprint('main', __name__)

# Initialize managers
report_manager = ReportManager(Config.JSON_FILE)
pollution_analyzer = PollutionAnalyzer()
cleanup_manager = CleanupManager(
    Config.BASE_DIR / "static" / "data" / "cleanups.json",
    Config.BASE_DIR / "static" / "data" / "teams.json"
)
rewards_manager = RewardsManager(
    Config.BASE_DIR / "static" / "data" / "rewards.json",
    Config.BASE_DIR / "static" / "data" / "badges.json"
)

@main.route("/")
def index():
    """Redirect to landing page."""
    return redirect(url_for("main.landing"))

@main.route("/landing")
def landing():
    """Display the landing page."""
    # Get user info from session if logged in
    user_logged_in = "user_id" in session
    user_email = session.get("email") if user_logged_in else None
    user_username = session.get("username") if user_logged_in else None
    
    return render_template("landing.html", 
                         user_logged_in=user_logged_in,
                         user_email=user_email,
                         user_username=user_username)

@main.route("/upload", methods=["GET"])
def upload_form():
    """Display the upload form."""
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in to report pollution", "error")
        return redirect(url_for("auth.login"))
    
    # Get user info from session
    user_email = session.get("email")
    user_username = session.get("username")
    
    return render_template("upload.html", user_email=user_email, user_username=user_username)

@main.route("/upload", methods=["POST"])
def upload():
    """Handle file upload and analysis."""
    try:
        # Validate file upload
        if "file" not in request.files:
            flash("No file uploaded", "error")
            return redirect(url_for("main.upload_form"))
        
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "error")
            return redirect(url_for("main.upload_form"))
        
        # Validate file extension
        allowed_extensions = Config.ALLOWED_EXTENSIONS
        if not file.filename or not file.filename.lower().endswith(tuple(f'.{ext}' for ext in allowed_extensions)):
            flash(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}", "error")
            return redirect(url_for("main.upload_form"))
        
        # Get form data
        name = request.form.get("name", "Anonymous").strip()
        email = request.form.get("email", "").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        
        # Validate required fields
        if not name or not email or not latitude or not longitude:
            flash("All fields are required", "error")
            return redirect(url_for("main.upload_form"))
        
        # Validate coordinates
        is_valid, coord_error = LocationUtils.validate_coordinates(latitude, longitude)
        if not is_valid:
            flash(coord_error, "error")
            return redirect(url_for("main.upload_form"))
        
        # Save file with reporter name prefix
        filename = secure_filename(f"{name}_{file.filename}")
        filepath = Path(Config.UPLOAD_FOLDER) / filename
        file.save(filepath)
        
        # Analyze image using Gemini AI
        analysis_result = pollution_analyzer.analyze_image(str(filepath))
        score = analysis_result["score"]
        analysis = analysis_result["analysis"]
        
        # Get location name
        location_name = LocationUtils.reverse_geocode(latitude, longitude)
        
        # Calculate points
        points = PollutionAnalyzer.calculate_points(score)
        
        # Create and save report
        report = Report(
            filename=filename,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            score=score,
            analysis=analysis,
            reporter_name=name,
            reporter_email=email,
            points=points
        )
        
        # Add report and get updated total points
        total_points = report_manager.add_report(report)
        
        # Award points to reporter
        rewards_manager.award_points(email, points, "reporter")
        
        # Create cleanup report automatically
        cleanup_report_id = cleanup_manager.create_cleanup_report(report.to_dict())
        
        # Get user info from session
        user_email = session.get("email")
        user_username = session.get("username")
        
        # Render result page
        return render_template(
            "result.html",
            filename=filename,
            score=score,
            analysis=analysis,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            points=points,
            total_points=total_points,
            severity_level=PollutionAnalyzer.get_severity_level(score),
            color_class=PollutionAnalyzer.get_color_class(score),
            ai_source=analysis_result.get("source", "Unknown"),
            cleanup_report_id=cleanup_report_id,
            user_email=user_email,
            user_username=user_username
        )
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("main.upload_form"))

@main.route("/dashboard")
def dashboard():
    """Display user dashboard with reports."""
    # Check if user is logged in
    if "user_id" not in session:
        flash("Please log in to view your dashboard", "error")
        return redirect(url_for("auth.login"))
    
    # Get user info from session
    user_email = session.get("email")
    user_username = session.get("username")
    
    # Show all reports for logged-in users
    email = user_email
    
    user_reports = report_manager.get_user_reports(email)
    total_points = report_manager.get_user_total_points(email)
    
    # Get user rewards
    user_rewards = rewards_manager.get_user_stats(email)
    
    return render_template(
        "dashboard.html",
        email=email,
        reports=user_reports,
        total_points=total_points,
        user_rewards=user_rewards,
        user_email=user_email,
        user_username=user_username
    ) 