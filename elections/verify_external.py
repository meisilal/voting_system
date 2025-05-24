from firebase_config import db

def upload_eligible_voters(election_id, voter_list):
    """
    Upload a list of eligible voters to Firestore under the given election_id.
    voter_list should be a list of dicts with keys like 'uid', 'name', 'id_number'.
    """
    try:
        batch = db.batch()
        for voter in voter_list:
            # Each voter is stored by their uid
            doc_ref = db.collection('eligibility').document(election_id).collection('approved_voters').document(voter['uid'])
            batch.set(doc_ref, voter)
        batch.commit()
        return True
    except Exception as e:
        print(f"Error uploading voter list: {e}")
        return False

def is_voter_eligible(election_id, voter_uid):
    """
    Check if a voter is eligible for the election by verifying if their uid
    exists in the approved_voters subcollection of the election eligibility document.
    Returns True if eligible, False otherwise.
    """
    try:
        doc_ref = db.collection('eligibility').document(election_id).collection('approved_voters').document(voter_uid)
        doc = doc_ref.get()
        return doc.exists
    except Exception as e:
        print(f"Error checking voter eligibility: {e}")
        return False
