from models import *

from flask import Flask, jsonify, abort, request
from datetime import datetime

users = [
    User(1, "alice", "pass123", "Alice Smith", "alice@example.com"),
    User(2, "bob", "secret", "Bob Jones", "bob@example.com"),
    User(3, "user2", "password", "Bob Jones", "bob@example.com")
]

categories = [
    Category(1, "Black Tea", "All kinds of black tea"),
    Category(2, "Green Tea", "All kinds of green tea"),
    Category(3, "Herbal Tea", "All kinds of herbal tea"),
    Category(4, "White Tea", "All kinds of white tea"),
    Category(5, "Rooibos Tea", "All kinds of rooibos tea"),
    Category(6, "Infusers", "All kinds of infusers"),
    Category(7, "Tea Cups", "All kinds of cups"),
    Category(8, "Tea Pods", "All kinds of pods"),
]

products = [
    Product(1, 1, "Darjeeling Classic", "Premium Darjeeling black tea leaves.", "1599", "black-tea"),
    Product(2, 1, "Assam Bold", "Strong and malty Assam tea for mornings.", "1399", "black-tea"),
    Product(3, 1, "Earl Grey", "Black tea with bergamot flavor.", "1499", "black-tea"),
    Product(4, 1, "English Breakfast", "Classic British black tea blend.", "1299", "black-tea"),
    Product(5, 1, "Ceylon Sunrise", "Bright and brisk black tea from Sri Lanka.", "1449", "black-tea"),
    Product(6, 1, "Russian Caravan", "Smoky black tea blend.", "1549", "black-tea"),
    Product(7, 1, "Lapsang Souchong", "Smoked black tea from China.", "1699", "black-tea"),
    Product(8, 2, "Sencha Green", "Traditional Japanese green tea.", "1399", "green-tea"),
    Product(9, 2, "Matcha Powder", "High-grade ceremonial matcha.", "2299", "green-tea"),
    Product(10, 2, "Genmaicha", "Green tea with roasted brown rice.", "1499", "green-tea"),
    Product(11, 2, "Gunpowder Green", "Rolled pellets of Chinese green tea.", "1349", "green-tea"),
    Product(12, 2, "Jasmine Green", "Floral green tea with jasmine petals.", "1499", "green-tea"),
    Product(13, 2, "Dragon Well", "Smooth and nutty Chinese green tea.", "1999", "green-tea"),
    Product(14, 3, "Chamomile Calm", "Soothing herbal tea with chamomile flowers.", "1299", "herbal-tea"),
    Product(15, 3, "Peppermint Pure", "Refreshing peppermint herbal infusion.", "1199", "herbal-tea"),
    Product(16, 3, "Hibiscus Burst", "Tart and vibrant hibiscus petals.", "1399", "herbal-tea"),
    Product(17, 3, "Lemon Ginger", "Zesty and warming herbal blend.", "1499", "herbal-tea"),
    Product(18, 3, "Turmeric Glow", "Spicy turmeric and pepper blend.", "1549", "herbal-tea"),
    Product(19, 3, "Rose Petal Infusion", "Delicate herbal tea with rose petals.", "1449", "herbal-tea"),
    Product(20, 4, "White Peony", "Mild white tea with a floral aroma.", "1799", "white-tea"),
    Product(21, 4, "Silver Needle", "Premium white tea with young buds.", "2299", "white-tea"),
    Product(22, 4, "White Jasmine", "White tea blended with jasmine flowers.", "1899", "white-tea"),
    Product(23, 4, "Peach White", "White tea with natural peach flavor.", "1699", "white-tea"),
    Product(24, 4, "Coconut White", "Tropical twist on white tea.", "1749", "white-tea"),
    Product(25, 5, "Classic Rooibos", "Earthy and smooth caffeine-free tea.", "1399", "rooibos"),
    Product(26, 5, "Vanilla Rooibos", "Sweet vanilla blended with rooibos.", "1499", "rooibos"),
    Product(27, 5, "Spiced Rooibos", "Cinnamon and clove rooibos blend.", "1549", "rooibos"),
    Product(28, 5, "Honeybush Harmony", "Naturally sweet and soothing.", "1399", "rooibos"),
    Product(29, 5, "Citrus Rooibos", "Zesty rooibos with lemon and orange peel.", "1499", "rooibos"),
    Product(30, 6, "Classic Infuser Ball", "Simple steel mesh ball infuser.", "499", "infusers"),
    Product(31, 6, "Silicone Leaf Infuser", "Colorful and fun silicone infuser.", "699", "infusers"),
    Product(32, 6, "Glass Tube Infuser", "Elegant glass tea infuser.", "1299", "infusers"),
    Product(33, 6, "Tea Spoon Infuser", "Scoop and steep tool.", "799", "infusers"),
    Product(34, 6, "Mug Lid Infuser", "Combo infuser and lid for mugs.", "899", "infusers"),
    Product(35, 7, "Porcelain Tea Cup", "Classic white tea cup.", "999", "tea-cups"),
    Product(36, 7, "Double Wall Glass", "Insulated glass cup.", "1299", "tea-cups"),
    Product(37, 7, "Cast Iron Cup", "Heavy-duty cup with Japanese design.", "1499", "tea-cups"),
    Product(38, 7, "Travel Tea Mug", "Spill-proof and insulated.", "1799", "tea-cups"),
    Product(39, 7, "Matcha Bowl", "Ceramic bowl for matcha.", "1999", "tea-cups"),
    Product(40, 8, "Earl Grey Pod", "Convenient pod with black tea and bergamot.", "799", "tea-pots"),
    Product(41, 8, "Green Tea Pod", "Quick-brew green tea pod.", "749", "tea-pots"),
    Product(42, 8, "Chai Spice Pod", "Spicy chai in pod form.", "849", "tea-pots"),
    Product(43, 8, "Mint Herbal Pod", "Refreshing herbal mint in a pod.", "749", "tea-pots"),
    Product(44, 8, "Peach White Pod", "Light white tea with peach.", "849", "tea-pots"),
    Product(45, 8, "Rooibos Vanilla Pod", "Sweet rooibos pod blend.", "799", "tea-pots"),
    Product(46, 2, "Iced Green Tea", "Cold brew green tea option.", "1399", "green-tea"),
    Product(47, 3, "Herbal Detox", "Cleansing herbal tea blend.", "1499", "herbal-tea"),
    Product(48, 4, "Berry White", "White tea with berry flavors.", "1599", "white-tea"),
    Product(49, 5, "Rooibos Latte Mix", "Rooibos blend for lattes.", "1699", "rooibos"),
    Product(50, 6, "Infuser Mug Set", "Mug with built-in infuser.", "1999", "infusers"),
]

orders = [
    Order(1, 1, datetime.now().isoformat(), 12499, "Alice Smith", "123 Main St", "Apt 4", "Visa", "4111111111111111", "12/25"),
    Order(2, 2, datetime.now().isoformat(), 12499, "Bob Jones", "123 Main St", "Apt 4", "Visa", "4111111111111111", "12/25")
]

order_items = [
    OrderItem(1, 1, 1, 1),
    OrderItem(2, 2, 1, 5),
    OrderItem(3, 3, 1, 3),
    OrderItem(4, 4, 1, 7),
    OrderItem(5, 5, 1, 1),
    OrderItem(6, 6, 1, 4),
    OrderItem(7, 7, 1, 4),
    OrderItem(8, 1, 1, 2),
    OrderItem(9, 2, 1, 17),
    OrderItem(10, 5, 1, 14),
    OrderItem(11, 8, 1, 3),
    OrderItem(12, 10, 1, 1),
    OrderItem(13, 14, 2, 1),
    OrderItem(14, 15, 2, 1),
    OrderItem(15, 14, 2, 5),
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