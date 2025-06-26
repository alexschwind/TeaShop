from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route("/api/pay", methods=["POST"])
def simulate_payment():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount")

    if user_id is None or amount is None:
        return jsonify({"error": "Missing user_id or amount"}), 400

    # Simulate payment success (you can make this random or conditional)
    success = random.randint(1, 100) <= 80

    if success:
        print(f"✅ Payment successful for user {user_id}, amount: {amount} cents")
        return jsonify({"success": True}), 200
    else:
        print(f"❌ Payment failed for user {user_id}, amount: {amount} cents")
        return jsonify({"success": False}), 402

if __name__ == "__main__":
    app.run(port=5010)
