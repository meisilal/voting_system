from firebase_config import db
from datetime import datetime

def create_election(election_data):
    try:
        # election_data = { "title": "School Council", "type": "school", "start_date": "...", ... }
        election_ref = db.collection('elections').document()
        election_data["created_at"] = datetime.utcnow().isoformat()
        election_data["election_id"] = election_ref.id
        election_ref.set(election_data)
        return election_ref.id
    except Exception as e:
        print(f"Error creating election: {e}")
        return None

def get_all_elections():
    try:
        elections = db.collection('elections').stream()
        return [doc.to_dict() for doc in elections]
    except Exception as e:
        print(f"Error fetching elections: {e}")
        return []

def get_election(election_id):
    try:
        doc = db.collection('elections').document(election_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error fetching election: {e}")
        return None