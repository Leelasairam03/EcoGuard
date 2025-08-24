import os
from pathlib import Path

class Config:
    """Application configuration class."""
    
    # Base directory
    BASE_DIR = Path(__file__).parent
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2025'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File upload settings
    UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Data storage
    JSON_FILE = BASE_DIR / "static" / "data" / "reports.json"
    
    # Gemini AI settings - PUT YOUR ACTUAL API KEY HERE
    GEMINI_API_KEY = "AIzaSyDgxiIQR2NMIEp2UaMpdde2uoNT61kA9DM"  # Replace with your real API key
    GEMINI_MODEL = 'gemini-1.5-flash'
    ANALYSIS_CONFIDENCE_THRESHOLD = float(os.environ.get('ANALYSIS_CONFIDENCE_THRESHOLD', '0.7'))
    
    # Analysis settings (fallback)
    DEFAULT_ANALYSIS_SCORE = 75
    DEFAULT_ANALYSIS_TEXT = "Moderate waste spotted in the uploaded image."
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure JSON file exists
        if not Config.JSON_FILE.exists():
            with open(Config.JSON_FILE, "w") as f:
                f.write("[]") 