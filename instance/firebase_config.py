import os
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = os.getenv("FIREBASE_CREDENTIALS", "instance/firebase_key.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()
