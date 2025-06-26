from flask import Flask, request, jsonify

class CartItem:
    def __init__(self, product_id: int, quantity: int):
        self.product_id = int(product_id)
        self.quantity = int(quantity)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
        }

# id: [cart_items]
carts = {} 

def find_by_id(items, id):
    return next((item for item in items if item.product_id == id), None)

app = Flask(__name__)

@app.route("/api/cart/<id>", methods=["GET"])
def get_cart(id):
    user_cart = carts.get(id, [])
    print(f"getting user cart for user {id}: ", user_cart)
    return jsonify([i.to_dict() for i in user_cart]), 200

@app.route("/api/cart/add", methods=["POST"])
def add_item():
    data = request.get_json()
    product_id = int(data.get("product_id"))
    user_id = str(data.get("id"))

    user_cart = carts.get(user_id, [])

    for item in user_cart:
        if item.product_id == product_id:
            item.quantity += 1
            carts[user_id] = user_cart
            return jsonify({
                    "success": "Increased quantity of item by one."
                }), 200
        
    user_cart.append(CartItem(product_id, 1))
    carts[user_id] = user_cart
    return jsonify({
        "success": "Added new item to cart."
    }), 200

@app.route("/api/cart/update", methods=["POST"])
def update_item():
    data = request.get_json()

    cart_items = data.get("cart_items")
    user_id = str(data.get("id"))

    user_cart = carts.get(user_id, [])

    print(cart_items)
    
    for key, val in cart_items.items():
        item = next((item for item in user_cart if item.product_id == int(key)), None)
        if item:
            item.quantity = int(val)

    carts[user_id] = user_cart

    return jsonify({
        "success": "cart updated."
    })

@app.route("/api/cart/remove", methods=["POST"])
def remove_item():
    data = request.get_json()
    product_id = int(data.get("product_id"))
    user_id = str(data.get("id"))

    user_cart = carts.get(user_id, [])
    user_cart = [item for item in user_cart if item.product_id != product_id]
    carts[user_id] = user_cart
        
    return jsonify({
        "success": "Item removed from cart."
    }), 200

@app.route("/api/cart/reset", methods=["POST"])
def reset():
    data = request.get_json()
    user_id = str(data.get("id"))
    carts[user_id] = []
        
    return jsonify({
        "success": "Reset."
    }), 200

@app.route("/api/cart/upgrade", methods=["POST"])
def upgrade():
    data = request.get_json()
    old_id = str(data.get("old_id"))
    new_id = str(data.get("new_id"))

    print("upgrading cart from ", old_id, "to ", new_id)
    print("before: ", carts)
    user_cart = carts.get(old_id, [])
    carts[old_id] = []
    carts[new_id] = user_cart
    
    print("after: ", carts)
    return jsonify({
        "success": "Reset."
    }), 200