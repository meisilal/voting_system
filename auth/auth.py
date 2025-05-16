from flask import Blueprint, request, redirect, flash, session, render_template
from firebase_admin import auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        id_token = request.form.get('id_token')
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            session['user'] = uid
            flash("Login successful.")
            return redirect("/")
        except Exception as e:
            flash(f"Authentication failed: {str(e)}", "danger")
            return redirect("/login")
    return render_template("login.html")

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out.")
    return redirect("/login")