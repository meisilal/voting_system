from firebase_config import db

def register_voter(data):
    try:
        db.collection('voters').document(data['uid']).set(data)
    except Exception as e:
        print(f"Error registering voter: {e}")

def get_voter(uid):
    try:
        doc_ref = db.collection("voters").document(uid)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
    except Exception as e:
        print(f"Error fetching voter data: {e}")
        return None
