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
    OrderItem(2, 2, 1, 1)
]

def find_by_id(items, id):
    return next((item for item in items if item.id == id), None)

def next_id(items):
    return max((item.id for item in items), default=0) + 1

def get_product(product_id: int):
    response = requests.get(f"http://product:5000/api/products/{product_id}")
    response.raise_for_status()

    data = response.json()
    return data

def get_products(product_ids: list[int]):
    products = []

    for id in product_ids:
        products.append(get_product(id))
    
    return products

app = Flask(__name__)

@app.route("/api/orders/<int:user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    user_orders = [order.to_dict() for order in orders if order.user_id == user_id]
    return jsonify(user_orders)

@app.route("/api/orders", methods=["POST"])
def place_order():
    try:
        data = request.get_json()

        order = data.get("order")
        user_id = int(data.get("user_id"))

        # 1. Get cart items
        cart_resp = requests.get(f"http://cart:5000/api/cart/{user_id}")
        cart_resp.raise_for_status()
        cart_items = cart_resp.json()

        # 2. Check + reserve inventory
        reserved_items = []
        for item in cart_items:
            check_payload = {
                "product_id": item["product_id"],
                "quantity": item["quantity"]
            }
            check_resp = requests.post("http://inventory:5000/api/inventory/check_and_reserve", json=check_payload)
            if check_resp.status_code != 200:
                # Rollback any already reserved stock
                for r in reserved_items:
                    requests.post("http://inventory:5000/api/inventory/release", json=r)
                return jsonify({"error": f"Insufficient stock for product {item['product_id']}"}), 400
            reserved_items.append(check_payload)


        # 3. Get product prices
        product_ids = [int(i["product_id"]) for i in cart_items]
        prod_resp = requests.post("http://product:5000/api/products/bulk", json={"ids": product_ids})
        prod_resp.raise_for_status()
        products = prod_resp.json()
        price_map = {int(p["id"]): int(p["price_in_cents"]) for p in products}

        # 4. Calculate total
        total_price = sum(int(item["quantity"]) * price_map[int(item["product_id"])] for item in cart_items)

        # 5. Simulate payment
        pay_resp = requests.post("http://payment:5000/api/pay", json={
            "user_id": user_id,
            "amount": total_price
        })
        if pay_resp.status_code != 200:
            for r in reserved_items:
                requests.post("http://inventory:5000/api/inventory/release", json=r)
            return jsonify({"error": "Payment failed"}), 402

        # 6. Store order
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

        # 7. Store order items
        item_id = next_id(order_items)
        for o in cart_items:
            order_items.append(OrderItem(item_id, order_id=new_order.id, **o))
            item_id += 1

        # 8. Dispatch shipping
        ship_resp = requests.post("http://shipping:5000/api/shipping/dispatch", json={
            "order_id": new_order.id,
            "address": {
                "name": new_order.address_name,
                "line1": new_order.address1,
                "line2": new_order.address2
            }
        })
        ship_data = ship_resp.json()
        shipping_id = ship_data.get("shipping_id")
        new_order.shipping_id = shipping_id

        orders.append(new_order)

        # 9. Reset cart
        requests.post("http://cart:5000/api/cart/reset", json={"id": user_id})

        # 10. Send email notification
        user_resp = requests.get(f"http://user:5000/api/users/{user_id}")
        if user_resp.status_code == 200:
            user_data = user_resp.json()
            email = user_data.get("email", f"user{user_id}@example.com")  # fallback email
            email_payload = {
                "user_id": user_id,
                "email": email,
                "subject": "Your order has been placed!",
                "message": f"Thank you! Your order #{new_order.id} is being processed."
            }
            requests.post("http://notification:5000/api/email/send", json=email_payload)

        return jsonify({"success": True, "order_id": new_order.id}), 200

    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500