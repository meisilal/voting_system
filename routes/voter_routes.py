from flask import Blueprint
from register import handle_registration

voter_bp = Blueprint("voter_bp", __name__)

voter_bp.add_url_rule("/register", view_func=handle_registration, methods=["GET", "POST"])