from flask import request, render_template, redirect, flash
from models.voter import register_voter

def handle_registration():
    if request.method == "POST":
        name = request.form['name']
        id_number = request.form['id_number']
        data = {"name": name, "id_number": id_number}
        register_voter(data)
        flash("Voter registered successfully.")
        return redirect("/register")
    return render_template("register.html")