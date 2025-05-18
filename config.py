import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
