from flask import  Flask
from config import Config
from firebase_admin import credentials, initialize_app
from routes.voter_routes import voter_bp
from routes.register import register_bp

app = Flask(__name__)
app.config.fom_object(Config)

cred = credentials.Certificate("firebase_key.json")
initialize_app(cred)

app.register_blueprint(register_bp)
app.register_blueprint(voter_bp)

if __name__ == "__main__":
    app.run(debug=True)