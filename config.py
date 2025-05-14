import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    FIREBASE_DB_URL = "https://votingsystem-d8c1c.firebaseio.com"
    