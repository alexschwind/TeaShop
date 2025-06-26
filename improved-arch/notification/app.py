from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

EMAIL_LOG_FILE = "sent_emails.log"

@app.route("/api/email/send", methods=["POST"])
def send_email():
    data = request.get_json()
    user_id = data.get("user_id")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    if not all([user_id, email, subject, message]):
        return jsonify({"error": "Missing email fields"}), 400

    print(f"📨 Email to {email} [User {user_id}]")
    print(f"Subject: {subject}")
    print(f"Message: {message}\n")

    log_entry = (
        f"[{datetime.now().isoformat()}] To: {email} (User {user_id})\n"
        f"Subject: {subject}\n"
        f"Message:\n{message}\n"
        f"{'-'*60}\n"
    )
    try:
        with open(EMAIL_LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"⚠️ Failed to write to log file: {e}")


    return jsonify({"sent": True}), 200
