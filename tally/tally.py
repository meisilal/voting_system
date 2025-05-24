from flask import Blueprint, request, render_template, flash, redirect, session
from firebase_config import db

tally_bp = Blueprint('tally', __name__)

@tally_bp.route('/tally', methods=['GET', 'POST'])
def tally_votes():
    try:
        # Fetch all elections for dropdown
        elections = db.collection('elections').stream()
        election_options = [e.to_dict() for e in elections]
    except Exception as e:
        flash(f"Error loading elections: {e}", "danger")
        election_options = []

    if request.method == 'POST':
        election_id = request.form.get('election_id')
        if not election_id:
            flash('Please select an election.', 'warning')
            return redirect("/tally")

        try:
            # Fetch all votes for the given election
            votes_ref = db.collection('votes').where('election_id', '==', election_id)
            votes = votes_ref.stream()

            tally_result = {}

            for vote in votes:
                vote_data = vote.to_dict()
                position = vote_data.get('position')
                candidate = vote_data.get('candidate')

                if position and candidate:
                    if position not in tally_result:
                        tally_result[position] = {}
                    tally_result[position][candidate] = tally_result[position].get(candidate, 0) + 1

            return render_template(
                "tally.html",
                tally=tally_result,
                election_id=election_id,
                election_options=election_options
            )

        except Exception as e:
            flash(f"Error tallying votes: {e}", "danger")
            return redirect("/tally")

    # GET request
    return render_template("tally.html", tally=None, election_options=election_options)
