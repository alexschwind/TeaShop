from flask import Flask, request, jsonify
from datetime import datetime
import requests

class OrderItem:
    def __init__(self, id: int, product_id: int, order_id: int, quantity: int):
        self.id = int(id)
        self.product_id = int(product_id)
        self.order_id = int(order_id)
        self.quantity = int(quantity)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "order_id": self.order_id,
            "quantity": self.quantity,
        }
            
class Order:
    def __init__(self, id: int, user_id: int, time: str, total_price_in_cents: int, address_name: str,
                 address1: str, address2: str, credit_card_company: str, credit_card_number: str, credit_card_expiry: str, shipping_id=None):
        self.id = int(id)
        self.user_id = int(user_id)
        self.time = time
        self.total_price_in_cents = int(total_price_in_cents)
        self.address_name = address_name
        self.address1 = address1
        self.address2 = address2
        self.credit_card_company = credit_card_company
        self.credit_card_number = credit_card_number
        self.credit_card_expiry = credit_card_expiry
        self.shipping_id = shipping_id

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "time": self.time,
            "total_price_in_cents": self.total_price_in_cents,
            "address_name": self.address_name,
            "address1": self.address1,
            "address2": self.address2,
            "credit_card_company": self.credit_card_company,
            "credit_card_number": self.credit_card_number,
            "credit_card_expiry": self.credit_card_expiry,
            "shipping_id": self.shipping_id
        }
    
orders = [
    Order(1, 1, datetime.now().isoformat(), 12499, "Alice Smith", "123 Main St", "Apt 4", "Visa", "4111111111111111", "12/25", "1234"),
    Order(2, 2, datetime.now().isoformat(), 12499, "Bob Jones", "123 Main St", "Apt 4", "Visa", "4111111111111111", "12/25", "1234")
]

order_items = [
    OrderItem(1, 1, 1, 1),
    OrderItem(2, 2, 1, 1),
    OrderItem(3, 2, 2, 1),
    OrderItem(4, 3, 2, 1),
    OrderItem(5, 5, 2, 3),
    OrderItem(6, 6, 2, 2),
    OrderItem(7, 7, 2, 3),
    OrderItem(8, 8, 2, 1),
]

def find_by_id(items, id):
    return next((item for item in items if item.id == id), None)

def next_id(items):
    return max((item.id for item in items), default=0) + 1

app = Flask(__name__)

@app.route("/api/orders/<int:user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    user_orders = [order.to_dict() for order in orders if order.user_id == user_id]
    return jsonify(user_orders)

@app.route("/api/orderitems", methods=["GET"])
def get_order_items():
    items = [item.to_dict() for item in order_items]
    return jsonify(items)

@app.route("/api/orders/set_shipping_id", methods=["POST"])
def set_shipping_id():
    try:
        data = request.get_json()

        # Store order
        order_id = data.get("order_id")
        shipping_id = data.get("shipping_id")
        
        order = find_by_id(orders, int(order_id))
        if order is None:
            raise Exception()
        order.shipping_id = shipping_id # TODO does this work or is this just a copy?
        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500

@app.route("/api/orders", methods=["POST"])
def create_order():
    try:
        data = request.get_json()

        # Store order
        order = data.get("order")
        user_id = data.get("user_id")
        total_price = data.get("total_price")
        new_order = Order(
            id=next_id(orders),
            user_id=user_id,
            time=datetime.now().isoformat(),
            total_price_in_cents=total_price,
            address_name=order["address_name"],
            address1=order["address1"],
            address2=order["address2"],
            credit_card_company=order["credit_card_company"],
            credit_card_number=order["credit_card_number"],
            credit_card_expiry=order["credit_card_expiry"],
        )

        # Store order items
        cart_items = data.get("order_items")
        item_id = next_id(order_items)
        for o in cart_items:
            order_items.append(OrderItem(item_id, order_id=new_order.id, **o))
            item_id += 1

        orders.append(new_order)

        return jsonify({"success": True, "order_id": new_order.id}), 200

    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500

@app.route("/api/place_order", methods=["POST"])
def place_order():
    try:
        data = request.get_json()

        order = data.get("order")
        user_id = int(data.get("user_id"))

        return jsonify({"success": True, "order_id": new_order.id}), 200

    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500