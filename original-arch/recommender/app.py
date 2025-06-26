import random
import requests
from flask import Flask, jsonify, request

# needs to periodically retrain

response = requests.get("http://persistence:5000/products")
response.raise_for_status()
products = response.json()
product_ids = [p["id"] for p in products if "id" in p]

app = Flask(__name__)

@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    if not product_ids:
        return jsonify({"error": "No products available"}), 503
    
    num_recommendations = request.args.get("num", 3, type=int)

    recommended = random.sample(product_ids, min(num_recommendations, len(product_ids)))
    return jsonify(recommended)