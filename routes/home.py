from flask import Blueprint, session, render_template, redirect, flash

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home():
    # Get user role from session, default to 'voter' if not found
    role = session.get('role', 'voter')

    # If no user logged in (no role), redirect to login
    if 'user' not in session:
        flash("Please log in to access the home page.", "warning")
        return redirect("/login")

    if role == "admin":
        return render_template("admin_home.html")
    else:
        return render_template("voter_home.html")
