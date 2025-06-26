import random
import requests
from flask import Flask, jsonify, request

stocks = {}

# init stock randomly
counter = 5
while counter > 0:
    try:
        response = requests.get("http://product:5000/api/products")
        response.raise_for_status()
        products = response.json()
        for p in products:
            id = p.get("id")
            quantity = random.randint(0, 10)
            stocks[id] = quantity
        break
    except Exception:
        counter -= 1
        continue

app = Flask(__name__)

@app.route("/api/inventory/<int:product_id>", methods=["GET"])
def get_stock(product_id):
    stock = stocks.get(product_id, 0)
    return jsonify({"product_id": product_id, "stock": stock})

@app.route("/api/inventory/check_and_reserve", methods=["POST"])
def check_and_reserve():
    data = request.get_json()
    product_id = int(data.get("product_id"))
    quantity = int(data.get("quantity"))

    if stocks.get(product_id, 0) >= quantity:
        stocks[product_id] -= quantity
        return jsonify({"success": True, "reserved": quantity}), 200
    else:
        return jsonify({"success": False, "available": stocks.get(product_id, 0)}), 400

@app.route("/api/inventory/release", methods=["POST"])
def release_stock():
    data = request.get_json()
    product_id = int(data.get("product_id"))
    quantity = int(data.get("quantity"))

    stocks[product_id] = stocks.get(product_id, 0) + quantity
    return jsonify({"success": True, "restored": quantity}), 200

