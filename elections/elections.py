from flask import Blueprint, request, render_template, flash, redirect, url_for
from firebase_config import db
from datetime import datetime
from blockchain.blockchain import create_block, get_latest_block

elections_bp = Blueprint('election', __name__)

@elections_bp.route('/', methods=['GET'])
def list_elections():
    try:
        elections = db.collection('elections').stream()
        election_list = [doc.to_dict() for doc in elections]
        return render_template('elections/list.html', elections=election_list)
    except Exception as e:
        flash(f"Error fetching elections: {str(e)}", "danger")
        return render_template('list.html', elections=[])

@elections_bp.route('/<election_id>', methods=['GET'])
def view_election(election_id):
    try:
        doc = db.collection('elections').document(election_id).get()
        if doc.exists:
            election = doc.to_dict()
            return render_template('elections/view.html', election=election)
        flash("Election not found.", "warning")
        return redirect(url_for('election.list_elections'))
    except Exception as e:
        flash(f"Error fetching election: {str(e)}", "danger")
        return redirect(url_for('election.list_elections'))

@elections_bp.route('/create', methods=['GET', 'POST'])
def create_election():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            election_type = request.form.get('type')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')

            # Collect positions from the form
            positions = []
            total_positions = int(request.form.get('total_positions', 0))

            for i in range(1, total_positions + 1):
                position_name = request.form.get(f'position_{i}')
                candidates_raw = request.form.get(f'candidates_{i}')  # comma-separated
                candidates = [c.strip() for c in candidates_raw.split(',') if c.strip()]
                if position_name and candidates:
                    positions.append({
                        "name": position_name,
                        "candidates": candidates
                    })

            election_data = {
                "title": title,
                "type": election_type,
                "start_date": start_date,
                "end_date": end_date,
                "positions": positions
            }

            election_ref = db.collection('elections').document()
            election_data["election_id"] = election_ref.id
            election_data["created_at"] = datetime.utcnow().isoformat()
            election_ref.set(election_data)

            # Blockchain log
            block_data = {
                "event": "election_created",
                "election_id": election_data["election_id"],
                "title": election_data["title"],
                "type": election_data["type"],
                "created_at": election_data["created_at"]
            }
            create_block(block_data)

            flash("Election created successfully.", "success")
            return redirect(url_for('election.list_elections'))
        except Exception as e:
            flash(f"Error creating election: {str(e)}", "danger")
            return redirect(url_for('election.create_election'))

    return render_template('create.html')

@elections_bp.route('/delete/<election_id>', methods=['POST'])
def delete_election(election_id):
    try:
        db.collection('elections').document(election_id).delete()
        flash(f"Election {election_id} deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting election: {str(e)}", "danger")
    return redirect(url_for('election.list_elections'))
