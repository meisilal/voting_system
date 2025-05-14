import firebase_admin
from firebase_admin import firestore

db = firestore.client()

def register_voter(data):
    voters_ref = db.collection("voters")
    voters_ref.add(data)