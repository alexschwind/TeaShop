from flask import Flask, request, jsonify
import requests

from models import *

app = Flask(__name__)

def get_user(username: str) -> User:
    response = requests.get(f"http://persistence:5000/users/by-username/{username}")
    response.raise_for_status()  # Raise error if request failed
    data = response.json()
    return User(**data)

def create_order(user_id: int, order: dict) -> Order:
    order["user_id"] = user_id
    response = requests.post(f"http://persistence:5000/orders", json=order)
    response.raise_for_status()  # Raise error if request failed
    data = response.json()
    return Order(**data)
    
def create_order_item(order_item: dict):
    response = requests.post(f"http://persistence:5000//order-items", json=order_item)
    response.raise_for_status()  # Raise error if request failed
    data = response.json()
    return OrderItem(**data)


@app.route("/is_logged_in", methods=["POST"])
def is_logged_in():
    session = request.get_json()
    session_id = session.get("session_id", None)

    if not session_id:
        return jsonify({
            "error": "no session found"
        }), 400
    
    return jsonify({
        "success": "session is correct"
    }), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    """
    {
        "username": str
        "password": str
        "session": dict
    }
    """

    username = data.get("username")
    password = data.get("password")
    session = data.get("session")
    
    user = get_user(username)

    if not user.password == password:
        return jsonify({
            "error": "wrong password"
        }), 400
    
    session["session_id"] = "123456"
    session["user_id"] = user.id
    
    return jsonify({
        "success": "user logged in.",
        "new_session": session
    }), 200

@app.route("/logout", methods=["POST"])
def logout():
    session = request.get_json()
    session.pop("session_id")
    session.pop("user_id")
    session.pop("order_items")
    return jsonify({
        "success": "user logged out.",
        "new_session": session
    }), 200

@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()

    order = create_order(int(data.get("user_id")), data.get("order"))

    order_items = [OrderItem(**o) for o in data.get("order_items")]
    for i in order_items:
        i.order_id = order.id
        create_order_item(i.to_dict())

    return jsonify({
        "success": "order created"
    }), 200

@app.route("/cart/add/", methods=["POST"])
def add_item():
    data = request.get_json()
    order_items = [OrderItem(**item) for item in data.get("order_items", [])]
    product_id = int(data.get("product_id"))

    for item in order_items:
        if item.product_id == product_id:
            item.quantity += 1
            return jsonify({
                    "new_order_items": [oi.to_dict() for oi in order_items]
                })
        
    order_items.append(OrderItem(-1, product_id, -1, 1))
    return jsonify({
        "new_order_items": [oi.to_dict() for oi in order_items]
    })

@app.route("/cart/update/", methods=["POST"])
def update_item():
    data = request.get_json()
    order_items = [OrderItem(**item) for item in data.get("order_items", [])]

    return jsonify({
        "new_order_items": [oi.to_dict() for oi in order_items]
    })

@app.route("/cart/remove/", methods=["POST"])
def remove_item():
    data = request.get_json()
    order_items = [OrderItem(**item) for item in data.get("order_items", [])]
    product_id = int(data.get("product_id"))

    new_order_items = [oi.to_dict() for oi in order_items if oi.product_id != product_id]
        
    return jsonify({
        "new_order_items": new_order_items
    })
