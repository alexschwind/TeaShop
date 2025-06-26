from models import *

from flask import Flask, jsonify, abort, request
from datetime import datetime

users = [
    User(1, "alice", "pass123", "Alice Smith", "alice@example.com"),
    User(2, "bob", "secret", "Bob Jones", "bob@example.com")
]

categories = [
    Category(1, "Books", "All kinds of books"),
    Category(2, "Electronics", "Gadgets and devices")
]

products = [
    Product(1, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(2, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(3, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(4, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(5, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(6, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(7, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(8, 1, "Python Book", "A book on Python.", "2500", "black-tea"),
    Product(9, 2, "Smartphone", "Latest model", "99999", "green-tea")
]

orders = [
    Order(1, 1, datetime.now().isoformat(), 12499, "Alice Smith", "123 Main St", "Apt 4", "Visa", "4111111111111111", "12/25"),
    Order(2, 2, datetime.now().isoformat(), 12499, "Bob Jones", "123 Main St", "Apt 4", "Visa", "4111111111111111", "12/25")
]

order_items = [
    OrderItem(1, 1, 1, 1),
    OrderItem(2, 2, 1, 1)
]

def find_by_id(items, id):
    return next((item for item in items if item.id == id), None)

def next_id(items):
    return max((item.id for item in items), default=0) + 1


app = Flask(__name__)

# ==== Collection Endpoints ====

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify([u.to_dict() for u in users])

@app.route("/categories", methods=["GET"])
def get_categories():
    return jsonify([c.to_dict() for c in categories])

@app.route("/products", methods=["GET"])
def get_products():
    return jsonify([p.to_dict() for p in products])

@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify([o.to_dict() for o in orders])

@app.route("/order-items", methods=["GET"])
def get_order_items():
    return jsonify([oi.to_dict() for oi in order_items])

# ==== Single Instance Endpoints ====

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    user = find_by_id(users, id)
    if user:
        return jsonify(user.to_dict())
    abort(404)

@app.route("/users/by-username/<username>", methods=["GET"])
def get_user_by_username(username):
    user = next((u for u in users if u.username == username), None)
    if user:
        return jsonify(user.to_dict())
    abort(404, description=f"User with username '{username}' not found.")

@app.route("/users/<int:id>/orders", methods=["GET"])
def get_orders_by_user(id):
    user = find_by_id(users, id)
    if not user:
        abort(404, description=f"User with id {id} not found.")

    user_orders = [order.to_dict() for order in orders if order.user_id == id]
    return jsonify(user_orders)

@app.route("/categories/<int:id>", methods=["GET"])
def get_category(id):
    category = find_by_id(categories, id)
    if category:
        return jsonify(category.to_dict())
    abort(404)

@app.route("/categories/<int:id>/products", methods=["GET"])
def get_products_by_category(id):
    matched_category = find_by_id(categories, id)
    if not matched_category:
        abort(404, description=f"Category with id {id} not found.")
    
    filtered_products = [p.to_dict() for p in products if p.category_id == id]
    return jsonify(filtered_products)

@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = find_by_id(products, id)
    if product:
        return jsonify(product.to_dict())
    abort(404)

@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    order = find_by_id(orders, id)
    if order:
        return jsonify(order.to_dict())
    abort(404)

@app.route("/order-items/<int:id>", methods=["GET"])
def get_order_item(id):
    item = find_by_id(order_items, id)
    if item:
        return jsonify(item.to_dict())
    abort(404)

# === POST Endpoints to Add New Instances ===

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    new_user = User(
        id=next_id(users),
        username=data["username"],
        password=data["password"],
        realname=data["realname"],
        email=data["email"]
    )
    users.append(new_user)
    return jsonify(new_user.to_dict()), 201

@app.route("/categories", methods=["POST"])
def create_category():
    data = request.json
    new_category = Category(
        id=next_id(categories),
        name=data["name"],
        description=data["description"]
    )
    categories.append(new_category)
    return jsonify(new_category.to_dict()), 201

@app.route("/products", methods=["POST"])
def create_product():
    data = request.json
    new_product = Product(
        id=next_id(products),
        category_id=data["category_id"],
        name=data["name"],
        description=data["description"],
        price_in_cents=data["price_in_cents"],
        img_name=data["img_name"]
    )
    products.append(new_product)
    return jsonify(new_product.to_dict()), 201

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json
    print("DATA", data)
    new_order = Order(
        id=next_id(orders),
        user_id=data["user_id"],
        time=data.get("time", datetime.now().isoformat()),
        total_price_in_cents=data["total_price_in_cents"],
        address_name=data["address_name"],
        address1=data["address1"],
        address2=data["address2"],
        credit_card_company=data["credit_card_company"],
        credit_card_number=data["credit_card_number"],
        credit_card_expiry=data["credit_card_expiry"]
    )
    orders.append(new_order)
    return jsonify(new_order.to_dict()), 201

@app.route("/order-items", methods=["POST"])
def create_order_item():
    data = request.json
    new_item = OrderItem(
        id=next_id(order_items),
        product_id=data["product_id"],
        order_id=data["order_id"],
        quantity=data["quantity"]
    )
    order_items.append(new_item)
    return jsonify(new_item.to_dict()), 201