import random
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    response = requests.get("http://product:5000/api/products")
    response.raise_for_status()
    products = response.json()
    product_ids = [p["id"] for p in products if "id" in p]
    if not product_ids:
        return jsonify({"error": "No products available"}), 503
    
    num_recommendations = request.args.get("num", 3, type=int)

    recommended = random.sample(product_ids, min(num_recommendations, len(product_ids)))
    return jsonify(recommended)