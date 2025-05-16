import firebase_admin
from firebase_admin import firestore
from firebase_config.firebase_config import db

db = firestore.client()

def register_voter(data):
    #data = {"uid": uid, "name": name,"id_number": id_number, "email": email}
    voters_ref = db.collection('voters')
    voters_ref.document(data['uid']).set(data)

def get_voter(uid):
    voter_doc = db.collection('voters').document(uid).get()
    if voter_doc.exists:
        return voter_doc.to_dict()
    return None