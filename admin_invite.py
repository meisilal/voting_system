import os
import random
import string
import firebase_admin
from firebase_admin import credentials, firestore
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Initialize Firebase Admin SDK (reuse your existing setup if any)
cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase_key.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# SendGrid setup (or any email provider)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Your verified sender email

def generate_code(length=8):
    """Generate a secure random alphanumeric code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def send_invite_email(to_email, code):
    """Send an admin invite email containing the code."""
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject="Your One-Time Admin Invite Code",
        html_content=f"""
        <p>Hello,</p>
        <p>You have been invited to register as an admin. Use the following one-time admin code during registration:</p>
        <h2>{code}</h2>
        <p>This code is valid for one use only.</p>
        """
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {to_email} with status {response.status_code}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def create_admin_invite(email):
    """Create an admin invite code, store in Firestore, and email it."""
    code = generate_code()
    invite_data = {
        "code": code,
        "used": False,
        "email": email  # Optional: tie code to email for extra validation
    }
    # Store in Firestore under collection 'admin_invites', doc id = code
    db.collection("admin_invites").document(code).set(invite_data)
    print(f"Invite code '{code}' created for {email}")
    send_invite_email(email, code)

if __name__ == "__main__":
    # Example: invite one or more emails
    emails_to_invite = [
        "admin1@example.com",
        "admin2@example.com",
    ]
    for email in emails_to_invite:
        create_admin_invite(email)
