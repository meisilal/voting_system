import hashlib
import time
from flask import Blueprint, request, redirect, flash, session, render_template, url_for
from firebase_config import db
from elections.verify_external import is_voter_eligible

vote_bp = Blueprint('vote', __name__)

# In-memory blockchain
blockchain = []

def create_block(data):
    previous_hash = blockchain[-1]['hash'] if blockchain else '0'
    block = {
        'index': len(blockchain) + 1,
        'timestamp': time.time(),
        'data': data,
        'previous_hash': previous_hash,
    }
    block_string = f"{block['index']}{block['timestamp']}{block['data']}{previous_hash}"
    block['hash'] = hashlib.sha256(block_string.encode()).hexdigest()
    blockchain.append(block)
    return block

def has_already_voted(voter_uid, election_id):
    votes = db.collection("votes") \
              .where("voter_uid", "==", voter_uid) \
              .where("election_id", "==", election_id) \
              .stream()
    return any(votes)

def add_vote_to_chain(voter_uid, election_id, vote_data):
    full_vote_data = {
        'voter_uid': voter_uid,
        'election_id': election_id,
        'position': vote_data['position'],
        'candidate': vote_data['candidate'],
        'timestamp': time.time()
    }

    block = create_block(full_vote_data)

    db.collection("votes").add({
        **full_vote_data,
        "block_hash": block['hash'],
        "block_index": block['index']
    })
    return True

@vote_bp.route('/', methods=['GET', 'POST'])
def cast_vote():
    if 'user' not in session:
        flash("Please login first.", "warning")
        return redirect("/auth/login")

    if request.method == "POST":
        try:
            voter_uid = session['user']
            election_id = request.form.get("election_id")

            if not election_id:
                flash("Election ID is missing.", "danger")
                return redirect(url_for("vote.cast_vote"))

            election_doc = db.collection('elections').document(election_id).get()
            if not election_doc.exists:
                flash("Selected election not found.", "danger")
                return redirect(url_for("vote.cast_vote"))

            selected_election = election_doc.to_dict()

            # Check if election is closed
            if selected_election.get("status") == "closed":
                flash("This election has already ended and is no longer accepting votes.", "danger")
                return redirect(url_for("vote.cast_vote"))

            # === New: Check voter eligibility ===
            if not is_voter_eligible(election_id, voter_uid):
                flash("You are not eligible to vote in this election.", "danger")
                return redirect(url_for("vote.cast_vote"))

            if has_already_voted(voter_uid, election_id):
                flash("You have already voted in this election.", "danger")
                return redirect(url_for("vote.cast_vote"))

            for position in selected_election.get('positions', []):
                position_key = f"vote_{election_id}_{position['name'].replace(' ', '_')}"
                candidate = request.form.get(position_key)

                if not candidate:
                    flash(f"Missing vote for {position['name']}.", "danger")
                    return redirect(url_for("vote.cast_vote"))

                add_vote_to_chain(voter_uid, election_id, {
                    "position": position['name'],
                    "candidate": candidate
                })

            flash("Your vote has been submitted successfully!", "success")
            return redirect(url_for("vote.cast_vote"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("vote.cast_vote"))

    # GET request: fetch and render elections that are not closed
    election_docs = db.collection('elections').stream()
    elections = []
    for doc in election_docs:
        data = doc.to_dict()
        if data.get("status") != "closed":
            data['election_id'] = doc.id
            elections.append(data)

    return render_template("vote.html", elections=elections)
