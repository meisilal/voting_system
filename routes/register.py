import firebase_admin
from flask import Blueprint, request, render_template, redirect, flash
from models.voter import register_voter
from firebase_admin import auth
from firebase_config import db  # Firestore client

register_bp = Blueprint('register', __name__)

def assign_role(uid, role):
    """Assign a role to the user in Firestore."""
    db.collection("roles").document(uid).set({"role": role})

def validate_admin_code(code, email):
    """Validate admin invite code and bind to email; mark as used."""
    docs = db.collection("admin_invites") \
        .where("code", "==", code) \
        .where("email", "==", email) \
        .limit(1).get()
    
    if not docs:
        return False  # No matching code/email found

    doc = docs[0]
    data = doc.to_dict()
    if data.get("used", True):
        return False  # Code already used

    # Mark code as used
    doc.reference.update({"used": True})
    return True

@register_bp.route('/', methods=['GET', 'POST'])
def handle_registration():
    if request.method == "POST":
        name = request.form['name']
        id_number = request.form['id_number']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'voter')  # Default role is 'voter'
        admin_code = request.form.get('admin_code', '').strip()

        try:
            # If registering as admin, verify admin_code with email binding
            if role == 'admin':
                if not admin_code:
                    flash("Admin code is required for admin registration.", "danger")
                    return render_template("register.html")
                
                if not validate_admin_code(admin_code, email):
                    flash("Invalid or already used admin code.", "danger")
                    return render_template("register.html")

            # Create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )

            # Save voter data (regardless of role for now)
            data = {
                "uid": user.uid,
                "name": name,
                "id_number": id_number,
                "email": email
            }
            register_voter(data)

            # Assign role
            assign_role(user.uid, role)

            flash(f"{role.capitalize()} registered successfully.", "success")
            return redirect("/login")

        except Exception as e:
            flash(f"Error registering user: {str(e)}", "danger")

    return render_template("register.html")
