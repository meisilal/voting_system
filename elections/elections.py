from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from firebase_config import db
from datetime import datetime
from blockchain.blockchain import create_block
import csv
import io
from verify_external import upload_eligible_voters

elections_bp = Blueprint('election', __name__)

def is_admin():
    return session.get('role') == 'admin'

def current_user():
    return session.get('user')

@elections_bp.route('/', methods=['GET'])
def list_elections():
    try:
        elections = db.collection('elections').stream()
        election_list = [doc.to_dict() for doc in elections]
        return render_template('list.html', elections=election_list)
    except Exception as e:
        flash(f"Error fetching elections: {str(e)}", "danger")
        return render_template('list.html', elections=[])

@elections_bp.route('/<election_id>', methods=['GET'])
def view_election(election_id):
    try:
        doc = db.collection('elections').document(election_id).get()
        if doc.exists:
            election = doc.to_dict()
            return render_template('view.html', election=election)
        flash("Election not found.", "warning")
        return redirect(url_for('election.list_elections'))
    except Exception as e:
        flash(f"Error fetching election: {str(e)}", "danger")
        return redirect(url_for('election.list_elections'))

@elections_bp.route('/create', methods=['GET', 'POST'])
def create_election():
    if not is_admin():
        flash("Unauthorized access.", "danger")
        return redirect("/auth/login")

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            election_type = request.form.get('type')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            positions = []
            total_positions = int(request.form.get('total_positions', 0))

            for i in range(1, total_positions + 1):
                position_name = request.form.get(f'position_{i}')
                candidates_raw = request.form.get(f'candidates_{i}')
                candidates = [c.strip() for c in candidates_raw.split(',') if c.strip()]
                if position_name and candidates:
                    positions.append({
                        "name": position_name,
                        "candidates": candidates
                    })

            election_ref = db.collection('elections').document()
            election_data = {
                "election_id": election_ref.id,
                "title": title,
                "type": election_type,
                "start_date": start_date,
                "end_date": end_date,
                "positions": positions,
                "status": "open",
                "created_by": current_user(),
                "created_at": datetime.utcnow().isoformat()
            }

            # Save election first
            election_ref.set(election_data)

            # Process uploaded CSV file of eligible voters (optional)
            voter_file = request.files.get('voter_file')
            if voter_file and voter_file.filename != '':
                stream = io.StringIO(voter_file.stream.read().decode("UTF8"), newline=None)
                csv_reader = csv.DictReader(stream)
                # Expect CSV column 'email' (or adapt if needed)
                voter_list = []
                for row in csv_reader:
                    email = row.get('email')
                    if email:
                        # Store at minimum email, you can extend as needed
                        voter_list.append({"uid": email.lower()})
                if voter_list:
                    success = upload_eligible_voters(election_ref.id, voter_list)
                    if not success:
                        flash("Warning: Failed to upload eligible voters list.", "warning")

            create_block({
                "event": "election_created",
                "election_id": election_data["election_id"],
                "title": election_data["title"],
                "type": election_data["type"],
                "created_at": election_data["created_at"]
            })

            flash("Election created successfully.", "success")
            return redirect(url_for('election.list_elections'))
        except Exception as e:
            flash(f"Error creating election: {str(e)}", "danger")
            return redirect(url_for('election.create_election'))

    return render_template('create.html')

@elections_bp.route('/delete/<election_id>', methods=['POST'])
def delete_election(election_id):
    if not is_admin():
        flash("Unauthorized access.", "danger")
        return redirect("/auth/login")

    try:
        election_ref = db.collection('elections').document(election_id)
        election_doc = election_ref.get()

        if not election_doc.exists:
            flash("Election not found.", "warning")
            return redirect(url_for('election.list_elections'))

        election = election_doc.to_dict()
        if election.get('created_by') != current_user():
            flash("You are not authorized to delete this election.", "danger")
            return redirect(url_for('election.list_elections'))

        election_ref.delete()

        # Optional: delete related votes
        votes = db.collection('votes').where('election_id', '==', election_id).stream()
        for vote in votes:
            db.collection('votes').document(vote.id).delete()

        # Delete eligibility list
        eligible_voters = db.collection('eligibility').document(election_id).collection('approved_voters').stream()
        for voter in eligible_voters:
            db.collection('eligibility').document(election_id).collection('approved_voters').document(voter.id).delete()

        flash(f"Election {election_id} and related data deleted.", "success")
    except Exception as e:
        flash(f"Error deleting election: {str(e)}", "danger")

    return redirect(url_for('election.list_elections'))
