from flask import Blueprint, request, redirect, flash, session, render_template
from firebase_admin import auth
from firebase_config import db  # Firestore client

auth_bp = Blueprint('auth', __name__)

def get_user_role(uid):
    """Fetch the user role from Firestore."""
    role_doc = db.collection("roles").document(uid).get()
    if role_doc.exists:
        role_data = role_doc.to_dict()
        return role_data.get("role", "voter")  # default to 'voter' if missing
    return "voter"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        id_token = request.form.get('id_token')
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            role = get_user_role(uid)

            # Store uid and role in session
            session['user'] = uid
            session['role'] = role

            flash("Login successful.", "success")

            # Redirect based on role (currently same for both, but can be customized)
            return redirect("/home")

        except Exception as e:
            flash(f"Authentication failed: {str(e)}", "danger")
            return redirect("/login")

    return render_template("login.html")

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash("Logged out.", "success")
    return redirect("/login")
