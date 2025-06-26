from temporalio import activity
import requests
import random
from shared import NotEnoughInventoryError, InsufficientFundsError

@activity.defn
async def get_cart_items(user_id):
    cart_resp = requests.get(f"http://cart:5000/api/cart/{user_id}")
    cart_resp.raise_for_status()
    cart_items = cart_resp.json()
    return cart_items

@activity.defn
async def check_and_reserve(cart_items):
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
            raise NotEnoughInventoryError(f"Not enought inventory for item {item.get("id")}")
        reserved_items.append(check_payload)

@activity.defn
async def get_total_price(cart_items):
    product_ids = [int(i["product_id"]) for i in cart_items]
    prod_resp = requests.post("http://product:5000/api/products/bulk", json={"ids": product_ids})
    prod_resp.raise_for_status()
    products = prod_resp.json()
    price_map = {int(p["id"]): int(p["price_in_cents"]) for p in products}

    # 4. Calculate total
    total_price = sum(int(item["quantity"]) * price_map[int(item["product_id"])] for item in cart_items)
    return total_price

@activity.defn
async def release_items(reserved_items):
    for r in reserved_items:
        resp = requests.post("http://inventory:5000/api/inventory/release", json=r)
        resp.raise_for_status()

@activity.defn
async def simulate_payment(user_id, total_price):
    if user_id is None or total_price is None:
        raise InsufficientFundsError("No valid payment data provided")

    # Simulate payment success (you can make this random or conditional)
    success = random.randint(1, 100) <= 80

    if not success:
        raise InsufficientFundsError("You dont have enough funds.")


@activity.defn
async def store_order(user_id, total_price, order_details, order_items): 
    order_resp = requests.post("http://order:5000/api/orders", json={
        "user_id": user_id,
        "total_price": total_price,
        "order": order_details,
        "order_items": order_items
    })
    order_resp.raise_for_status()
    data = order_resp.json()
    return data.get("order_id")

@activity.defn
async def dispatch_shipping(order_id, order_details): 
    ship_resp = requests.post("http://shipping:5000/api/shipping/dispatch", json={
        "order_id": order_id,
        "address": {
            "name": order_details.address_name,
            "line1": order_details.address1,
            "line2": order_details.address2
        }
    })
    ship_resp.raise_for_status()
    ship_data = ship_resp.json()
    shipping_id = ship_data.get("shipping_id")
    return shipping_id

@activity.defn
async def set_shipping_id(order_id, shipping_id): 
    resp = requests.post("http://order:5000/api/orders/set_shipping_id", json={
        "order_id": order_id,
        "shipping_id": shipping_id
    })
    resp.raise_for_status()

@activity.defn
async def reset_cart(user_id): 
    resp = requests.post("http://cart:5000/api/cart/reset", json={"id": user_id})
    resp.raise_for_status()

@activity.defn
async def get_user_email(user_id): 
    user_resp = requests.get(f"http://user:5000/api/users/{user_id}")
    user_resp.raise_for_status()
    user_data = user_resp.json()
    email = user_data.get("email", f"user{user_id}@example.com")  # fallback email
    return email

@activity.defn
async def send_email_notification(email, new_order_id): 
    print(f"📨 Email to {email}")
    print(f"Subject: Your order has been placed!")
    print(f"Message: Thank you! Your order #{new_order_id} is being processed.\n")