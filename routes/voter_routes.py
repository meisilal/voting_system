from flask import Blueprint, jsonify, session, flash, redirect
from models.voter import get_voter

voter_bp = Blueprint('voter', __name__)

@voter_bp.route('/voter')
def get_voter_info():
    if 'user' not in session:
        flash("Please login first.")
        return redirect("/login")
    uid = session['user']
    voter = get_voter(uid)
    if voter:
        return jsonify(voter)
    return jsonify({"error": "Voter not found"}), 404