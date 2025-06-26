from flask import Flask, render_template, redirect, session, flash, request, make_response
import requests
from math import ceil

from models import *

app = Flask(__name__)
app.secret_key = "123456789"

### PERSISTENCE ###
def get_category_list() -> list[Category]:
    response = requests.get(f"http://persistence:5000/categories")
    response.raise_for_status()  # Raise error if request failed

    data = response.json()
    categories = [Category(**item) for item in data]
    return categories

def get_category(category_id: int) -> Category:
    response = requests.get(f"http://persistence:5000/categories/{category_id}")
    response.raise_for_status()  # Raise error if request failed

    data = response.json()
    return Category(**data)

def get_products_for_category(category_id: int) -> list[Product]:
    response = requests.get(f"http://persistence:5000/categories/{category_id}/products")
    response.raise_for_status()  # Raise error if request failed

    data = response.json()
    products = [Product(**item) for item in data]
    return products

def get_product(product_id: int) -> Product:
    response = requests.get(f"http://persistence:5000/products/{product_id}")
    response.raise_for_status()  # Raise error if request failed

    data = response.json()
    return Product(**data)

def get_products(product_ids: list[int]) -> list[Product]:
    products = []

    for id in product_ids:
        products.append(get_product(id))
    
    
    return products

def get_user(user_id: int) -> User:
    response = requests.get(f"http://persistence:5000/users/{user_id}")
    response.raise_for_status()  # Raise error if request failed

    data = response.json()
    return User(**data)

def get_user_orders(user_id: int) -> list[Order]:
    response = requests.get(f"http://persistence:5000/users/{user_id}/orders")
    response.raise_for_status()  # Raise error if request failed

    data = response.json()
    orders = [Order(**item) for item in data]
    return orders

### IMAGE ###
def get_images(image_names: list[str]) -> dict[str, str]:
    query = ",".join(image_names)
    url = f"http://image:5000/images?names={query}"
    response = requests.get(url)
    response.raise_for_status()  # Raise error if request failed
    images_list = response.json()

    return images_list

def get_image(image_name) -> str:
    url = f"http://image:5000/images?names={image_name}"
    response = requests.get(url)
    response.raise_for_status()  # Raise error if request failed
    images_list = response.json()
    
    return images_list.get(image_name)

### RECOMMENDER ###
def get_recommendations():
    response = requests.get(f"http://recommender:5000/recommendations?num=3")
    response.raise_for_status()

    data = response.json()
    return [int(i) for i in data]

### AUTH ###
def is_logged_in() -> bool:
    session_data = dict(session)

    response = requests.post("http://auth:5000/is_logged_in", json=session_data)

    if response.status_code == 200:
        return True
    else:
        return False

def call_login(username, password):
    session_data = dict(session)

    data = {
        "username": username,
        "password": password,
        "session": session_data
    }

    response = requests.post("http://auth:5000/login", json=data)

    new_session_data = response.json().get("new_session")

    if response.status_code == 200:
        session.clear()
        session.update(new_session_data)
        return True
    
    else:
        return False

def call_logout():
    session_data = dict(session)

    response = requests.post("http://auth:5000/logout", json=session_data)

    new_session_data = response.json().get("new_session")

    if response.status_code == 200:
        session.clear()
        session.update(new_session_data)
        return True
    else:
        return False

def call_add_item_to_cart(product_id: int):
    session_data = dict(session)

    data = {
        "product_id": product_id,
        "order_items": session_data.get("order_items", [])
    }

    response = requests.post("http://auth:5000/cart/add", json=data)

    new_order_items = response.json().get("new_order_items")

    if response.status_code == 200:
        session.update({ "order_items": new_order_items})
        return True
    
    else:
        return False

def call_remove_item_from_cart(product_id):
    session_data = dict(session)

    data = {
        "product_id": product_id,
        "order_items": session_data.get("order_items", [])
    }

    print("sending:" + str(data))

    response = requests.post("http://auth:5000/cart/remove", json=data)

    new_order_items = response.json().get("new_order_items")

    print("receiving:" + str(new_order_items))

    if response.status_code == 200:
        session.update({ "order_items": new_order_items})
        return True
    
    else:
        return False

def call_update_cart(order_items: list[OrderItem]):
    data = {
        "order_items": [o.to_dict() for o in order_items]
    }

    response = requests.post("http://auth:5000/cart/update", json=data)

    new_order_items = response.json().get("new_order_items")

    if response.status_code == 200:
        session.update({ "order_items": new_order_items})
        return True
    
    else:
        return False

def call_place_order(firstname, lastname, address1, address2, cardtype, cardnumber, expirydate, total_price, order_items, user_id):
    data = {
        "order": {
            "address_name": firstname + " " + lastname,
            "address1": address1,
            "address2": address2,
            "total_price_in_cents": total_price,
            "credit_card_company": cardtype,
            "credit_card_number": cardnumber,
            "credit_card_expiry": expirydate
        },
        "order_items": [o.to_dict() for o in order_items],
        "user_id": user_id
    }

    response = requests.post("http://auth:5000/place_order", json=data)

    if response.status_code == 200:
        session.update({ "order_items": []})
        return True
    
    else:
        return False



def render_template_base(template, **context):
    login = is_logged_in()
    context["login"] = login
    return render_template(template, **context)

@app.route("/")
def index():

    category_list = get_category_list()
    return render_template_base("index.html", category_list=category_list)

@app.route("/profile")
def profile():

    login = is_logged_in()

    if not login:
        flash("You are not signed in.")
        return redirect("/login")

    category_list = get_category_list()

    user_id = int(session.get("user_id", -1))

    if user_id == -1:
        flash("You are not signed in.")
        return redirect("/")

    user = get_user(user_id)

    orders = get_user_orders(user_id)

    return render_template_base("profile.html", category_list=category_list, user=user, orders=orders)

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        referer = request.form.get("referer", None)

        success = call_login(username, password)

        if success:
            if referer:
                return redirect(referer)

            return redirect("/")
        
        else:
            flash('Invalid credentials. Please try again.')
            return render_template_base("login.html")
    
    if is_logged_in():
        flash("You are already logged in. Please sign out before loggin in.")
        return redirect("/")

    category_list = get_category_list()

    referer = request.referrer or ""

    return render_template_base("login.html", referer=referer, category_list=category_list)

@app.route("/logout")
def logout():
    if call_logout():
        flash("You have been logged out.")
        return redirect("/")
    
    flash("Logout failed.")
    return redirect("/")

@app.route("/category", methods=['GET', 'POST'])
def category():

    if request.method == 'POST':
        selected_number_of_products = request.form['number']
        session["selected_number_of_products"] = selected_number_of_products

    page = request.args.get('page', default=1, type=int)

    product_number_options = [1, 2, 3, 4, 5]
    selected_number_of_products = int(session.get("selected_number_of_products", 3))

    category_id = request.args.get('category', None, type=int)
    if not category_id:
        message = {
            "title": "Category not found",
            "text": "No category was provided."
        }
        return render_template_base("error.html", message=message)

    category = get_category(category_id)

    products = get_products_for_category(category_id)

    products_page = products[(0 + (page-1)*selected_number_of_products):(page*selected_number_of_products)]

    images = get_images([p.img_name for p in products_page])

    # Add the base64 image to the product dict
    for p in products_page:
        p.image = images.get(p.img_name)

    total_pages = ceil(len(products) / selected_number_of_products)
    pagination = []
    if page > 1:
        pagination.append("previous")
    for n in range(1, total_pages+1):
        pagination.append(n)
    if page < total_pages:
        pagination.append("next")

    category_list = get_category_list()

    return render_template_base("category.html", 
                                category_list=category_list,
                                category=category,
                                products=products_page,
                                pagination=pagination,
                                current_page_number=page,
                                product_number_options=product_number_options,
                                selected_number_of_products=selected_number_of_products
                                )

@app.route("/product")
def product():
    product_id = request.args.get('id', None, type=int)
    if not product_id:
        message = {
            "title": "Product not found",
            "text": "No product was provided."
        }
        return render_template_base("error.html", message=message)

    product = get_product(product_id)

    image = get_image(product.img_name)

    # Add the base64 image to the product dict
    product.image = image

    ads_ids = get_recommendations()
    """
    [
        <product_id>, ...
    ]
    """

    ads = get_products(ads_ids)

    ad_images = get_images([p.img_name for p in ads])

    # Add the base64 image to the product dict
    for p in ads:
        p.image = ad_images[p.img_name]

    ads = ads[:3]

    category_list = get_category_list()

    return render_template_base("product.html", category_list=category_list, product=product, ads=ads)

@app.route("/order")
def order():

    cart_items = session.get("order_items", [])

    if not cart_items:
        flash("You have no items in your cart.")
        return redirect("/")

    return render_template_base("order.html")

@app.route("/cart")
def cart():

    order_items = session.get("order_items", [])

    products = get_products([i.get("product_id") for i in order_items])

    products_map = {
        p.id : p for p in products
    }

    ads_ids = get_recommendations()
    """
    [
        <product_id>, ...
    ]
    """

    ads = get_products(ads_ids)

    ad_images = get_images([p.img_name for p in ads])
    """
    {
        "<image_name>": <image in base64> 
    }
    """

    # Add the base64 image to the product dict
    for p in ads:
        p.image = ad_images[p.img_name]

    ads = ads[:3]

    category_list = get_category_list()

    return render_template_base("cart.html", category_list=category_list, products=products_map, ads=ads, order_items=order_items)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("productid", type=int)

    success = call_add_item_to_cart(product_id)
    if success:
        flash("Product added to cart.")
        return redirect("/cart")
    else:
        flash("Failed to add product to cart.")
        return redirect("/cart")

@app.route("/update-cart", methods=["POST"])
def update_cart():
    data = session.get("order_items", [])
    order_items = [OrderItem(**item) for item in data]

    # remove item
    product_to_remove = request.form.get("remove_item")
    if product_to_remove:
        success = call_remove_item_from_cart(product_to_remove)
        if success:
            flash("Product removed from cart.")
            return redirect("/cart")
        
        else:
            flash("Failed to remove product from cart.")
            return redirect("/cart")


    # else update cart
    for item in order_items:
        if f"quantity_{item.product_id}" in request.form:
            item.quantity = request.form.get(f"quantity_{item.product_id}", type=int)

    success = call_update_cart(order_items)
    if success:
        flash("Cart updated.")
        return redirect("/cart")
    
    else:
        flash("Failed to update cart.")
        return redirect("/cart")

@app.route("/checkout", methods=["POST"])
def checkout():
    login = is_logged_in()

    if not login:
        response = make_response(redirect("/login"))
        response.headers["Referer"] = "/order"
        return response

    return redirect("/order")

@app.route("/place_order", methods=["POST"])
def place_order():
    required_fields = [
        "firstname", "lastname",
        "address1", "address2",
        "cardtype", "cardnumber", "expirydate"
    ]

    # Ensure all fields are present
    for field in required_fields:
        if field not in request.form or not request.form[field].strip():
            flash("Some entries are not provided.")
            return redirect("/order")

    # Extract values
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    address1 = request.form["address1"]
    address2 = request.form["address2"]
    cardtype = request.form["cardtype"]
    cardnumber = request.form["cardnumber"]
    expirydate = request.form["expirydate"]

    data = session.get("order_items", [])
    order_items = [OrderItem(**item) for item in data]

    products = get_products([i.product_id for i in order_items])

    products_map = {
        p.id : p.price_in_cents for p in products
    }

    total_price = 0
    for item in order_items:
        total_price += item.quantity * products_map[item.product_id]

    user_id = session.get("user_id")

    success = call_place_order(firstname, lastname, address1, address2, cardtype, cardnumber, expirydate, total_price, order_items, user_id)
    if success:
        return redirect("/")
    
    else:
        flash("Failed to confirm.")
        return redirect("/cart")
