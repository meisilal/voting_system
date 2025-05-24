from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from firebase_config import db

admin_elections_bp = Blueprint('admin_elections', __name__, url_prefix='/admin/elections')

def is_admin():
    return session.get('role') == 'admin'

def current_user():
    return session.get('user')

@admin_elections_bp.route('/', methods=['GET'])
def list_admin_elections():
    if not is_admin():
        flash("Unauthorized access.", "danger")
        return redirect("/auth/login")

    try:
        elections = db.collection('elections').stream()
        election_list = []
        for doc in elections:
            election = doc.to_dict()
            election['id'] = doc.id
            election_list.append(election)
    except Exception as e:
        flash(f"Error loading elections: {e}", "danger")
        election_list = []

    return render_template("admin_elections.html", elections=election_list)

@admin_elections_bp.route('/end/<election_id>', methods=['POST'])
def end_election(election_id):
    if not is_admin():
        flash("Unauthorized access.", "danger")
        return redirect("/auth/login")

    try:
        election_ref = db.collection('elections').document(election_id)
        election_doc = election_ref.get()
        if not election_doc.exists:
            flash("Election not found.", "danger")
            return redirect(url_for('admin_elections.list_admin_elections'))

        election = election_doc.to_dict()
        if election.get('created_by') != current_user():
            flash("You are not authorized to end this election.", "danger")
            return redirect(url_for('admin_elections.list_admin_elections'))

        election_ref.update({'status': 'closed'})
        flash("Election has been ended successfully.", "success")
    except Exception as e:
        flash(f"Error ending election: {e}", "danger")

    return redirect(url_for('admin_elections.list_admin_elections'))

@admin_elections_bp.route('/delete/<election_id>', methods=['POST'])
def delete_election(election_id):
    if not is_admin():
        flash("Unauthorized access.", "danger")
        return redirect("/auth/login")

    try:
        election_ref = db.collection('elections').document(election_id)
        election_doc = election_ref.get()
        if not election_doc.exists:
            flash("Election not found.", "danger")
            return redirect(url_for('admin_elections.list_admin_elections'))

        election = election_doc.to_dict()
        if election.get('created_by') != current_user():
            flash("You are not authorized to delete this election.", "danger")
            return redirect(url_for('admin_elections.list_admin_elections'))

        election_ref.delete()

        # Optional: delete related votes
        votes = db.collection('votes').where('election_id', '==', election_id).stream()
        for vote in votes:
            db.collection('votes').document(vote.id).delete()

        flash("Election and related votes deleted.", "success")
    except Exception as e:
        flash(f"Error deleting election: {e}", "danger")

    return redirect(url_for('admin_elections.list_admin_elections'))
