import requests
from flask import Flask, jsonify, request

# needs to periodically retrain

response = requests.get("http://persistence:5000//order-items")
response.raise_for_status()
order_items = response.json()
counts = {}
for item in order_items:
    p_id = item.get("product_id")
    counts[p_id] = counts.get(p_id, 0) + int(item.get("quantity", 1))

counts = sorted(counts.items(), key=lambda x: x[1])
counts = [x[0] for x in counts]

app = Flask(__name__)

@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    if not counts:
        return jsonify({"error": "No products available"}), 503
    
    num_recommendations = min(request.args.get("num", 3, type=int), len(counts))

    recommended = counts[:num_recommendations]
    return jsonify(recommended)