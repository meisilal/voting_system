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

def add_vote_to_chain(voter_uid, election_id, candidate):
    vote_data = {
        'voter_uid': voter_uid,
        'election_id': election_id,
        'candidate': candidate,
        'timestamp': time.time()
    }

    # Add vote to blockchain
    block = create_block(vote_data)

    # Store vote in Firebase Firestore
    db.collection("votes").add({
        "voter_uid": voter_uid,
        "election_id": election_id,
        "candidate": candidate,
        "timestamp": vote_data['timestamp'],
        "block_hash": block['hash'],
        "block_index": block['index']
    })
    return True

@vote_bp.route('/vote', methods=['GET', 'POST'])
def cast_vote():
    if 'user' not in session:
        flash("Please login first.")
        return redirect("/login")

    if request.method == "POST":
        election_id = request.form.get('election_id')
        candidate = request.form.get('candidate')
        voter_uid = session['user']

        success = add_vote_to_chain(voter_uid, election_id, candidate)
        if success:
            flash("Vote cast successfully.")
        else:
            flash("Failed to cast vote.")
        return redirect("/vote")

    return render_template("vote.html")
