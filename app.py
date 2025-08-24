import os
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from config import Config

def create_app(config_class=Config):
    """Application factory pattern for creating Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize configuration
    config_class.init_app(app)
    
    # Register blueprints
    from routes.main import main
    from routes.cleanup import cleanup
    from routes.auth import auth
    
    app.register_blueprint(main)
    app.register_blueprint(cleanup, url_prefix='/cleanup')
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)
