from flask import Flask, request, jsonify

app = Flask(__name__)

shipping_status_db = {}

@app.route("/api/shipping/dispatch", methods=["POST"])
def dispatch():
    data = request.get_json()
    order_id = data.get("order_id")
    address = data.get("address", {})

    if not order_id or not address:
        return jsonify({"error": "Missing order_id or address"}), 400

    shipping_id = f"SHIP{len(shipping_status_db) + 1}"
    shipping_status_db[shipping_id] = {
        "order_id": order_id,
        "status": "Processing",
        "address": address,
        "estimated_days": 3
    }

    print(f"📦 Dispatching order {order_id} to {address.get('name')}")
    return jsonify({
        "shipping_id": shipping_id,
        "status": "Processing",
        "estimated_days": 3
    }), 200

@app.route("/api/shipping/status/<shipping_id>", methods=["GET"])
def get_status(shipping_id):
    shipping_info = shipping_status_db.get(shipping_id)
    if not shipping_info:
        return jsonify({"error": "Shipping ID not found"}), 404
    return jsonify(shipping_info)

if __name__ == "__main__":
    app.run(port=5011)
