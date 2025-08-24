from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class Report:
    """Model class for pollution reports."""
    
    def __init__(self, filename: str, latitude: str, longitude: str, 
                 location_name: str, score: int, analysis: str, 
                 reporter_name: str, reporter_email: str, points: int = 0):
        self.filename = filename
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = location_name
        self.score = score
        self.analysis = analysis
        self.reporter_name = reporter_name
        self.reporter_email = reporter_email
        self.points = points
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON storage."""
        return {
            "filename": self.filename,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
            "score": self.score,
            "analysis": self.analysis,
            "reporter_name": self.reporter_name,
            "reporter_email": self.reporter_email,
            "points": self.points,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Report':
        """Create report instance from dictionary."""
        return cls(
            filename=data.get("filename", ""),
            latitude=data.get("latitude", ""),
            longitude=data.get("longitude", ""),
            location_name=data.get("location_name", ""),
            score=data.get("score", 0),
            analysis=data.get("analysis", ""),
            reporter_name=data.get("reporter_name", ""),
            reporter_email=data.get("reporter_email", ""),
            points=data.get("points", 0)
        )

class ReportManager:
    """Manager class for handling report operations."""
    
    def __init__(self, json_file_path: Path):
        self.json_file_path = json_file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists with proper structure."""
        if not self.json_file_path.exists():
            self.json_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.json_file_path, "w") as f:
                json.dump([], f, indent=2)
    
    def load_reports(self) -> List[Dict]:
        """Load all reports from JSON file."""
        try:
            with open(self.json_file_path, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_reports(self, reports: List[Dict]):
        """Save reports to JSON file."""
        with open(self.json_file_path, "w") as f:
            json.dump(reports, f, indent=2)
    
    def add_report(self, report: Report) -> int:
        """Add a new report and return total points for the user."""
        reports = self.load_reports()
        
        # Find existing user or create new one
        user = next((u for u in reports if u.get("email") == report.reporter_email), None)
        
        if user:
            user["reports"].append(report.to_dict())
            user["total_points"] += report.points
        else:
            reports.append({
                "name": report.reporter_name,
                "email": report.reporter_email,
                "reports": [report.to_dict()],
                "total_points": report.points
            })
        
        self.save_reports(reports)
        
        # Return updated total points for this user
        user_total_points = next((u["total_points"] for u in reports if u.get("email") == report.reporter_email), report.points)
        return user_total_points
    
    def get_user_reports(self, email: str) -> List[Dict]:
        """Get all reports for a specific user."""
        reports = self.load_reports()
        user = next((u for u in reports if u.get("email") == email), None)
        return user.get("reports", []) if user else []
    
    def get_user_total_points(self, email: str) -> int:
        """Get total points for a specific user."""
        reports = self.load_reports()
        user = next((u for u in reports if u.get("email") == email), None)
        return user.get("total_points", 0) if user else 0 