from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import random

class CleanupStatus:
    """Enum for cleanup status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CLEANED = "cleaned"
    VERIFIED = "verified"

class CleanupReport:
    """Model for cleanup reports with status tracking."""
    
    def __init__(self, report_id: str, pollution_report: Dict, status: str = CleanupStatus.PENDING):
        self.report_id = report_id
        self.pollution_report = pollution_report
        self.status = status
        self.assigned_team = None
        self.assigned_date = None
        self.start_date = None
        self.completion_date = None
        self.cleanup_notes = ""
        self.verification_photos = []
        self.cleanup_points = 0
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage."""
        return {
            "report_id": self.report_id,
            "pollution_report": self.pollution_report,
            "status": self.status,
            "assigned_team": self.assigned_team,
            "assigned_date": self.assigned_date,
            "start_date": self.start_date,
            "completion_date": self.completion_date,
            "cleanup_notes": self.cleanup_notes,
            "verification_photos": self.verification_photos,
            "cleanup_points": self.cleanup_points,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CleanupReport':
        """Create instance from dictionary."""
        instance = cls(data["report_id"], data["pollution_report"], data["status"])
        instance.assigned_team = data.get("assigned_team")
        instance.assigned_date = data.get("assigned_date")
        instance.start_date = data.get("start_date")
        instance.completion_date = data.get("completion_date")
        instance.cleanup_notes = data.get("cleanup_notes", "")
        instance.verification_photos = data.get("verification_photos", [])
        instance.cleanup_points = data.get("cleanup_points", 0)
        instance.created_at = data.get("created_at")
        instance.updated_at = data.get("updated_at")
        return instance

class CleanupTeam:
    """Model for cleanup teams."""
    
    def __init__(self, team_id: str, name: str, leader_email: str, members: List[str] = None):
        self.team_id = team_id
        self.name = name
        self.leader_email = leader_email
        self.members = members or []
        self.status = "available"  # available, busy, inactive
        self.current_task = None
        self.total_cleanups = 0
        self.total_points = 0
        self.rating = 5.0
        self.created_at = datetime.now().isoformat()
        self.last_activity = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage."""
        return {
            "team_id": self.team_id,
            "name": self.name,
            "leader_email": self.leader_email,
            "members": self.members,
            "status": self.status,
            "current_task": self.current_task,
            "total_cleanups": self.total_cleanups,
            "total_points": self.total_points,
            "rating": self.rating,
            "created_at": self.created_at,
            "last_activity": self.last_activity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CleanupTeam':
        """Create instance from dictionary."""
        instance = cls(data["team_id"], data["name"], data["leader_email"], data.get("members", []))
        instance.status = data.get("status", "available")
        instance.current_task = data.get("current_task")
        instance.total_cleanups = data.get("total_cleanups", 0)
        instance.total_points = data.get("total_points", 0)
        instance.rating = data.get("rating", 5.0)
        instance.created_at = data.get("created_at")
        instance.last_activity = data.get("last_activity")
        return instance

class CleanupManager:
    """Manager class for cleanup operations."""
    
    def __init__(self, cleanup_file: Path, teams_file: Path):
        self.cleanup_file = cleanup_file
        self.teams_file = teams_file
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure JSON files exist with proper structure."""
        self.cleanup_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.cleanup_file.exists():
            with open(self.cleanup_file, "w") as f:
                json.dump([], f, indent=2)
        
        if not self.teams_file.exists():
            with open(self.teams_file, "w") as f:
                json.dump([], f, indent=2)
    
    def load_cleanups(self) -> List[Dict]:
        """Load all cleanup reports."""
        try:
            with open(self.cleanup_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_cleanups(self, cleanups: List[Dict]):
        """Save cleanup reports to JSON file."""
        with open(self.cleanup_file, "w") as f:
            json.dump(cleanups, f, indent=2)
    
    def load_teams(self) -> List[Dict]:
        """Load all cleanup teams."""
        try:
            with open(self.teams_file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_teams(self, teams: List[Dict]):
        """Save teams to JSON file."""
        with open(self.teams_file, "w") as f:
            json.dump(teams, f, indent=2)
    
    def create_cleanup_report(self, pollution_report: Dict) -> str:
        """Create a new cleanup report."""
        cleanups = self.load_cleanups()
        
        # Generate unique report ID
        report_id = f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Create cleanup report
        cleanup_report = CleanupReport(report_id, pollution_report)
        cleanups.append(cleanup_report.to_dict())
        
        self.save_cleanups(cleanups)
        
        # Try to auto-assign team
        self.auto_assign_team(report_id)
        
        return report_id
    
    def auto_assign_team(self, report_id: str) -> Optional[str]:
        """Automatically assign an available team to a cleanup task."""
        cleanups = self.load_cleanups()
        teams = self.load_teams()
        
        # Find the cleanup report
        cleanup = next((c for c in cleanups if c["report_id"] == report_id), None)
        if not cleanup:
            return None
        
        # Find available teams
        available_teams = [t for t in teams if t["status"] == "available"]
        
        if not available_teams:
            return None
        
        # Select best team (highest rating, most experience)
        best_team = max(available_teams, key=lambda t: (t["rating"], t["total_cleanups"]))
        
        # Assign team
        cleanup["assigned_team"] = best_team["team_id"]
        cleanup["assigned_date"] = datetime.now().isoformat()
        cleanup["status"] = CleanupStatus.IN_PROGRESS
        cleanup["updated_at"] = datetime.now().isoformat()
        
        # Update team status
        best_team["status"] = "busy"
        best_team["current_task"] = report_id
        best_team["last_activity"] = datetime.now().isoformat()
        
        self.save_cleanups(cleanups)
        self.save_teams(teams)
        
        return best_team["team_id"]
    
    def create_team(self, name: str, leader_email: str, members: List[str] = None) -> str:
        """Create a new cleanup team."""
        teams = self.load_teams()
        
        # Generate unique team ID
        team_id = f"team_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Create team
        team = CleanupTeam(team_id, name, leader_email, members or [leader_email])
        teams.append(team.to_dict())
        
        self.save_teams(teams)
        return team_id
    
    def update_cleanup_status(self, report_id: str, status: str, notes: str = "", photos: List[str] = None):
        """Update cleanup status and add notes/photos."""
        cleanups = self.load_cleanups()
        teams = self.load_teams()
        
        cleanup = next((c for c in cleanups if c["report_id"] == report_id), None)
        if not cleanup:
            return False
        
        old_status = cleanup["status"]
        cleanup["status"] = status
        cleanup["cleanup_notes"] = notes
        cleanup["updated_at"] = datetime.now().isoformat()
        
        if photos:
            cleanup["verification_photos"].extend(photos)
        
        # Handle status-specific logic
        if status == CleanupStatus.IN_PROGRESS and not cleanup["start_date"]:
            cleanup["start_date"] = datetime.now().isoformat()
        
        elif status == CleanupStatus.CLEANED:
            cleanup["completion_date"] = datetime.now().isoformat()
            cleanup["cleanup_points"] = self._calculate_cleanup_points(cleanup)
            
            # Free up the team
            if cleanup["assigned_team"]:
                team = next((t for t in teams if t["team_id"] == cleanup["assigned_team"]), None)
                if team:
                    team["status"] = "available"
                    team["current_task"] = None
                    team["total_cleanups"] += 1
                    team["total_points"] += cleanup["cleanup_points"]
                    team["last_activity"] = datetime.now().isoformat()
        
        elif status == CleanupStatus.VERIFIED:
            # Award points to reporter
            self._award_reporter_points(cleanup["pollution_report"]["reporter_email"], 10)
        
        self.save_cleanups(cleanups)
        self.save_teams(teams)
        return True
    
    def submit_cleanup_verification(self, report_id: str, team_email: str, notes: str, 
                                   verification_photos: List[str], cleanup_score: int = None) -> Dict[str, Any]:
        """Submit cleanup verification with photos and analysis score."""
        cleanups = self.load_cleanups()
        teams = self.load_teams()
        
        cleanup = next((c for c in cleanups if c["report_id"] == report_id), None)
        if not cleanup:
            return {"success": False, "message": "Cleanup report not found"}
        
        # Verify team assignment
        if cleanup["assigned_team"]:
            team = next((t for t in teams if t["team_id"] == cleanup["assigned_team"]), None)
            if not team or team_email not in team["members"]:
                return {"success": False, "message": "Unauthorized: You are not assigned to this cleanup task"}
        
        # Update cleanup with verification data
        cleanup["cleanup_notes"] = notes
        cleanup["verification_photos"] = verification_photos
        cleanup["updated_at"] = datetime.now().isoformat()
        
        # Determine if cleanup was successful based on score
        if cleanup_score is not None:
            if cleanup_score <= 30:  # Low score means good cleanup
                cleanup["status"] = CleanupStatus.CLEANED
                cleanup["completion_date"] = datetime.now().isoformat()
                cleanup["cleanup_points"] = self._calculate_cleanup_points(cleanup)
                
                # Free up the team and award points
                if cleanup["assigned_team"]:
                    team = next((t for t in teams if t["team_id"] == cleanup["assigned_team"]), None)
                    if team:
                        team["status"] = "available"
                        team["current_task"] = None
                        team["total_cleanups"] += 1
                        team["total_points"] += cleanup["cleanup_points"]
                        team["last_activity"] = datetime.now().isoformat()
                
                self.save_cleanups(cleanups)
                self.save_teams(teams)
                
                return {
                    "success": True, 
                    "message": "Cleanup verified successfully! Task completed.",
                    "status": CleanupStatus.CLEANED,
                    "points_awarded": cleanup["cleanup_points"]
                }
            else:
                # High score means cleanup was not sufficient
                cleanup["status"] = CleanupStatus.IN_PROGRESS
                cleanup["cleanup_notes"] += f"\n[VERIFICATION FAILED] Score: {cleanup_score}. Cleanup incomplete, task continues."
                
                self.save_cleanups(cleanups)
                
                return {
                    "success": False, 
                    "message": "Cleanup verification failed. Task continues.",
                    "status": CleanupStatus.IN_PROGRESS,
                    "score": cleanup_score
                }
        
        self.save_cleanups(cleanups)
        return {"success": True, "message": "Verification submitted successfully"}
    
    def get_team_cleanup_tasks(self, team_email: str) -> List[Dict]:
        """Get cleanup tasks assigned to a specific team member."""
        cleanups = self.load_cleanups()
        teams = self.load_teams()
        
        team_tasks = []
        for cleanup in cleanups:
            if cleanup["assigned_team"]:
                team = next((t for t in teams if t["team_id"] == cleanup["assigned_team"]), None)
                if team and team_email in team["members"]:
                    team_tasks.append(cleanup)
        
        return team_tasks
    
    def _calculate_cleanup_points(self, cleanup: Dict) -> int:
        """Calculate points for cleanup completion."""
        base_points = 25
        severity_bonus = cleanup["pollution_report"]["score"] // 10  # Higher pollution = more points
        return base_points + severity_bonus
    
    def _award_reporter_points(self, email: str, points: int):
        """Award points to reporter for verified cleanup."""
        # This would integrate with the main report manager
        # For now, we'll just track it separately
        pass
    
    def get_cleanup_stats(self) -> Dict:
        """Get overall cleanup statistics."""
        cleanups = self.load_cleanups()
        teams = self.load_teams()
        
        total_reports = len(cleanups)
        pending = len([c for c in cleanups if c["status"] == CleanupStatus.PENDING])
        in_progress = len([c for c in cleanups if c["status"] == CleanupStatus.IN_PROGRESS])
        cleaned = len([c for c in cleanups if c["status"] == CleanupStatus.CLEANED])
        verified = len([c for c in cleanups if c["status"] == CleanupStatus.VERIFIED])
        
        total_teams = len(teams)
        available_teams = len([t for t in teams if t["status"] == "available"])
        busy_teams = len([t for t in teams if t["status"] == "busy"])
        
        return {
            "total_reports": total_reports,
            "pending": pending,
            "in_progress": in_progress,
            "cleaned": cleaned,
            "verified": verified,
            "total_teams": total_teams,
            "available_teams": available_teams,
            "busy_teams": busy_teams
        }
