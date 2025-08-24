from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.auth import AuthManager
from config import Config
from pathlib import Path

auth = Blueprint('auth', __name__)

# Initialize auth manager
auth_manager = AuthManager(Config.BASE_DIR / "static" / "data" / "users.json")

@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("auth/login.html")
        
        # Authenticate user
        user = auth_manager.authenticate_user(email, password)
        
        if user:
            # Store user info in session
            session["user_id"] = user.user_id
            session["email"] = user.email
            session["username"] = user.username
            session["user_type"] = user.user_type
            
            flash(f"Welcome back, {user.username}!", "success")
            
            # Redirect based on user type
            if user.user_type == "admin":
                return redirect(url_for("cleanup.cleanup_dashboard"))
            else:
                return redirect(url_for("main.dashboard", email=user.email))
        else:
            flash("Invalid email or password", "error")
    
    return render_template("auth/login.html")

@auth.route("/logout")
def logout():
    """Handle user logout."""
    # Clear session
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("main.landing"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash("All fields are required", "error")
            return render_template("auth/register.html")
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("auth/register.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template("auth/register.html")
        
        # Check if user already exists
        existing_user = auth_manager.get_user_by_email(email)
        if existing_user:
            flash("User with this email already exists", "error")
            return render_template("auth/register.html")
        
        # Create new user
        new_user = auth_manager.create_user(username, email, password)
        
        if new_user:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Registration failed. Please try again.", "error")
    
    return render_template("auth/register.html")

@auth.route("/profile")
def profile():
    """Display user profile."""
    if "user_id" not in session:
        flash("Please log in to view your profile", "error")
        return redirect(url_for("auth.login"))
    
    user = auth_manager.get_user_by_email(session["email"])
    if not user:
        session.clear()
        flash("User not found", "error")
        return redirect(url_for("auth.login"))
    
    return render_template("auth/profile.html", user=user)
