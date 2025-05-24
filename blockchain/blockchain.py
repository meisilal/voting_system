import hashlib
import json
from datetime import datetime
import os
from firebase_config import db  # make sure this import matches your setup

# In-memory blockchain
blockchain = []

CHAIN_FILE = "blockchain.json"

# --- Blockchain Core Functions ---

def create_block(data):
    previous_hash = blockchain[-1]['hash'] if blockchain else '0'
    block = {
        'index': len(blockchain) + 1,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data,
        'previous_hash': previous_hash,
    }
    # Use JSON serialization with sorted keys for consistent hashing
    block_string = f"{block['index']}{block['timestamp']}{json.dumps(block['data'], sort_keys=True)}{previous_hash}"
    block['hash'] = hashlib.sha256(block_string.encode()).hexdigest()
    blockchain.append(block)
    save_chain_to_file()  # persist after adding a block
    return block

def add_vote_to_chain(voter_uid, election_id, vote_data):
    full_vote_data = {
        'voter_uid': voter_uid,
        'election_id': election_id,
        'position': vote_data['position'],
        'candidate': vote_data['candidate'],
        'timestamp': datetime.utcnow().isoformat()
    }

    block = create_block(full_vote_data)

    # Save to Firebase
    db.collection("votes").add({
        **full_vote_data,
        "block_hash": block['hash'],
        "block_index": block['index']
    })

    return block

def get_latest_block():
    return blockchain[-1] if blockchain else None

def is_chain_valid():
    for i in range(1, len(blockchain)):
        current = blockchain[i]
        previous = blockchain[i - 1]

        # Recalculate hash from stored data
        block_string = f"{current['index']}{current['timestamp']}{json.dumps(current['data'], sort_keys=True)}{current['previous_hash']}"
        recalculated_hash = hashlib.sha256(block_string.encode()).hexdigest()

        if current['hash'] != recalculated_hash:
            return False, f"Invalid hash at block {i}"

        if current['previous_hash'] != previous['hash']:
            return False, f"Broken chain at block {i}"

    return True, "Blockchain is valid"

# --- Persistence Functions ---

def save_chain_to_file(filename=CHAIN_FILE):
    try:
        with open(filename, "w") as f:
            json.dump(blockchain, f, indent=4)
    except Exception as e:
        print(f"Error saving blockchain: {e}")

def load_chain_from_file(filename=CHAIN_FILE):
    global blockchain
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                blockchain = json.load(f)
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            blockchain = []
    else:
        blockchain = []

# Load blockchain on startup
load_chain_from_file()
