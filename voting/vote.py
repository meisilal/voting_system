from flask import Blueprint, request, redirect, flash, session, render_template
from blockchain.blockchain import add_vote_to_chain
from firebase_admin import auth

vote_bp = Blueprint('vote', __name__)

@vote_bp.route('/vote', methods=['GET', 'POST'])
def cast_vote():
    if 'user' not in session:
        flash("Please login first.")
        return redirect("/login")

    if request.method == "POST":
        vote = request.form.get('vote')
        voter_uid = session['user']

        # Optionally validate vote data here

        success = add_vote_to_chain(voter_uid, vote)
        if success:
            flash("Vote cast successfully.")
        else:
            flash("Failed to cast vote.")
        return redirect("/vote")

    return render_template("vote.html")