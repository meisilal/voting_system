from firebase_config import db

def check_eligibility(uid, election_id):
    try:
        # Check if voter exists
        voter_doc = db.collection('voters').document(uid).get()
        if not voter_doc.exists:
            return False, "Voter not found."

        # Check if voter is approved for the election
        eligibility_doc = db.collection('eligibility').document(election_id).collection('approved_voters').document(uid).get()
        if eligibility_doc.exists:
            return True, "Voter is eligible."
        else:
            return False, "Voter not eligible for this election."
    except Exception as e:
        return False, f"Error checking eligibility: {str(e)}"
