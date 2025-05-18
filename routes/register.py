import firebase_admin
from flask import Blueprint, request, render_template, redirect, flash
from models.voter import register_voter
from firebase_admin import auth
from elections.eligibility_check import check_eligibility

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def handle_registration():
    if request.method == "POST":
        name = request.form['name']
        id_number = request.form['id_number']
        email = request.form['email']
        password = request.form['password']
        election_type = request.form['election_type']

        eligible = check_eligibility(id_number, election_type)
        if not eligible:
            flash("You are not eligible to vote in this election.")
            return render_template("register.html")

        try:
            #create user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            #Save additional voter data to Firestore
            data = {
                "uid": user.uid,
                "name": name,
                "id_number": id_number,
                "email" : email,
                "election_type" : election_type
            } 
            register_voter(data)

            flash("Voter registered successfully.")
            return redirect("/register")
        except Exception as e:
            flash(f"Error registering voter: {str(e)}", "danger")
        
    return render_template("register.html")