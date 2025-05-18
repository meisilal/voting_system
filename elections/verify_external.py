from firebase_config import db

def upload_eligible_voters(election_id, voter_list):
    try:
        batch = db.batch()
        for voter in voter_list:
            # voter = { "uid": "...", "name": "...", "id_number": "..." }
            doc_ref = db.collection('eligibility').document(election_id).collection('approved_voters').document(voter['uid'])
            batch.set(doc_ref, voter)
        batch.commit()
        return True
    except Exception as e:
        print(f"Error uploading voter list: {e}")
        return False
