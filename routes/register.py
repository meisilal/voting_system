import firebase_admin
from flask import Blueprint, request, render_template, redirect, flash
from models.voter import register_voter
from firebase_admin import auth

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def handle_registration():
    if request.method == "POST":
        name = request.form['name']
        id_number = request.form['id_number']
        email = request.form['email']
        password = request.form['password']

        try:
            #create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            #Save additional voter data (e.g., ID number) to Firestore
            data = {
                "uid": user.uid,
                "name": name,
                "id_number": id_number,
                "email" : email
            } 
            register_voter(data)

            flash("Voter registered successfully.")
            return redirect("/register")
        except Exception as e:
            flash(f"Error registering voter: {str(e)}", "danger")
            return render_template("register.html")
        
    return render_template("register.html")