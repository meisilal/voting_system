import firebase_admin
from flask import Blueprint, request, redirect, flash, session
from firebase_admin import auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        #Handles Firebase authentication
        #Validates and creates session if successful
        flash("Login functionality not yet implemented.", "info")
        return redirect('/login')
    return "Login Page Placeholder"

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect('/login')