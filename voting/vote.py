import hashlib
import time
from flask import Blueprint, request, redirect, flash, session, render_template
from firebase_config import db

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
    """
    Checks if the voter has already voted in the given election.
    """
    votes = db.collection("votes") \
              .where("voter_uid", "==", voter_uid) \
              .where("election_id", "==", election_id) \
              .stream()
    return any(votes)  # True if any vote documents exist

def add_vote_to_chain(voter_uid, election_id, vote_data):
    full_vote_data = {
        'voter_uid': voter_uid,
        'election_id': election_id,
        'position': vote_data['position'],
        'candidate': vote_data['candidate'],
        'timestamp': time.time()
    }

    # Blockchain block
    block = create_block(full_vote_data)

    # Firebase write
    db.collection("votes").add({
        **full_vote_data,
        "block_hash": block['hash'],
        "block_index": block['index']
    })
    return True

@vote_bp.route('/vote', methods=['GET', 'POST'])
def cast_vote():
    if 'user' not in session:
        flash("Please login first.", "warning")
        return redirect("/auth/login")  # Adjusted to your auth login route

    if request.method == "POST":
        try:
            voter_uid = session['user']
            election_id = request.form.get('election_id')

            if not election_id:
                flash("Please select an election.", "danger")
                return redirect("/vote")

            # Get election document directly by ID
            election_doc = db.collection('elections').document(election_id).get()
            if not election_doc.exists:
                flash("Selected election not found.", "danger")
                return redirect("/vote")

            selected_election = election_doc.to_dict()

            if has_already_voted(voter_uid, election_id):
                flash("You have already voted in this election.", "danger")
                return redirect("/vote")

            # Collect votes for all positions
            for position in selected_election.get('positions', []):
                position_name = position['name'].replace(" ", "_")
                vote_key = f"vote_{election_id}_{position_name}"
                candidate = request.form.get(vote_key)

                if not candidate:
                    flash(f"Missing vote for position {position['name']}.", "danger")
                    return redirect("/vote")

                add_vote_to_chain(voter_uid, election_id, {
                    "position": position['name'],
                    "candidate": candidate
                })

            flash("All votes cast successfully.", "success")
            return redirect("/vote")

        except Exception as e:
            flash(f"Error submitting vote: {str(e)}", "danger")
            return redirect("/vote")

    # GET request - list all elections
    elections = db.collection('elections').stream()
    election_list = [doc.to_dict() for doc in elections]
    return render_template("vote.html", elections=election_list)
