from flask import Flask
from config import Config
from datetime import datetime  # <-- Import datetime

# Import blueprints
from routes.voter_routes import voter_bp
from routes.register import register_bp
from voting.vote import vote_bp
from tally.tally import tally_bp
from auth.auth import auth_bp
from elections.elections import elections_bp
from routes.home import home_bp

# Import firebase db to ensure it's initialized once
from firebase_config import db  


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(register_bp, url_prefix='/register')
    app.register_blueprint(voter_bp, url_prefix='/voter')
    app.register_blueprint(vote_bp, url_prefix='/vote')
    app.register_blueprint(tally_bp, url_prefix='/tally')
    app.register_blueprint(elections_bp, url_prefix='/elections')
    app.register_blueprint(home_bp)

    # Make `now` globally available in all templates
    @app.context_processor
    def inject_now():
        # Return the callable datetime.now (not datetime.now())
        return {'now': datetime.now}

    # Define the root route
    @app.route('/')
    def home():
        return "Welcome to the Voting System!"
    
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    print()
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
