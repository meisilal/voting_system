from flask import Blueprint, request, redirect, flash, session, render_template
from voting.vote import add_vote_to_chain

vote_bp = Blueprint('vote', __name__)

@vote_bp.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user' not in session:
        flash("Please login first.")
        return redirect("/login")

    if request.method == "POST":
        vote = request.form.get('vote')
        election_id = request.form.get('election_id')  # optional for filtering votes by type
        voter_uid = session['user']

        success = add_vote_to_chain(voter_uid, vote, election_id)
        if success:
            flash("Vote cast successfully.")
        else:
            flash("Failed to cast vote.")
        return redirect("/vote")

    return render_template("vote.html")
