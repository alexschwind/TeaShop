import requests
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

popular_items_cache = []

@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    global popular_items_cache
    try:
        response = requests.get("http://order:5000/api/orderitems")
        response.raise_for_status()
        order_items = response.json()
        counts = {}
        for item in order_items:
            p_id = item.get("product_id")
            counts[p_id] = counts.get(p_id, 0) + item.get("quantity", 1)
        
        counts = sorted(counts.items(), key=lambda x: x[1])
        counts = [x[0] for x in counts]
        print("MOST POPULAR ITEMS: ", counts)
        popular_items_cache = counts.copy()
        
        num_recommendations = min(request.args.get("num", 3, type=int), len(counts))
        recommended = counts[:num_recommendations]
        return jsonify(recommended)
    except Exception:
        if len(popular_items_cache) == 0:
            abort(500)
        num_recommendations = min(request.args.get("num", 3, type=int), len(popular_items_cache))
        recommended = popular_items_cache[:num_recommendations]
        return jsonify(recommended)