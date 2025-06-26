from flask import Flask, request, jsonify, abort

class Category:
    def __init__(self, id: int, name: str, description: str):
        self.id = int(id)
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
    
class Product:
    def __init__(self, id: int, category_id: int, name: str, description: str, price_in_cents: str, img_name: str):
        self.id = int(id)
        self.category_id = int(category_id)
        self.name = name
        self.description = description
        self.price_in_cents = int(price_in_cents)
        self.img_name = img_name

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "price_in_cents": self.price_in_cents,
            "img_name": self.img_name
        }

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

def find_by_id(items, id):
    return next((item for item in items if item.id == id), None)

def next_id(items):
    return max((item.id for item in items), default=0) + 1

app = Flask(__name__)

@app.route("/api/categories", methods=["GET"])
def get_categories():
    return jsonify([c.to_dict() for c in categories])

@app.route("/api/products", methods=["GET"])
def get_products():
    return jsonify([p.to_dict() for p in products])

@app.route("/api/categories/<int:id>", methods=["GET"])
def get_category(id):
    category = find_by_id(categories, id)
    if category:
        return jsonify(category.to_dict())
    abort(404)

@app.route("/api/categories/<int:id>/products", methods=["GET"])
def get_products_by_category(id):
    matched_category = find_by_id(categories, id)
    if not matched_category:
        abort(404, description=f"Category with id {id} not found.")
    
    filtered_products = [p.to_dict() for p in products if p.category_id == id]
    return jsonify(filtered_products)

@app.route("/api/products/<int:id>", methods=["GET"])
def get_product(id):
    product = find_by_id(products, id)
    if product:
        return jsonify(product.to_dict())
    abort(404)

@app.route("/api/products/bulk", methods=["POST"])
def get_products_bulk():
    data = request.get_json()
    if not data or "ids" not in data:
        abort(400, description="Missing 'ids' in request body")

    ids = data["ids"]
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        abort(400, description="'ids' must be a list of integers")

    result = [p.to_dict() for p in products if p.id in ids]
    return jsonify(result)