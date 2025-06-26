from flask import Flask, render_template, redirect, session, flash, request, make_response, Response
import requests
from math import ceil
import uuid

app = Flask(__name__)
app.secret_key = "123456789"

def get_images(image_names: list[str]) -> dict[str, str]:
    query = ",".join(image_names)
    url = f"http://image:5000/api/images?names={query}"
    response = requests.get(url)
    response.raise_for_status()  # Raise error if request failed
    images_list = response.json()

    return images_list

def get_image(image_name) -> str:
    url = f"http://image:5000/api/images?names={image_name}"
    response = requests.get(url)
    response.raise_for_status()  # Raise error if request failed
    images_list = response.json()
    
    return images_list.get(image_name)

def get_recommendations(num=3):
    response = requests.get(f"http://recommender:5000/api/recommendations?num={num}")
    response.raise_for_status()

    data = response.json()
    return [int(i) for i in data]

def render_template_base(template, **context):
    login = "user_id" in session
    context["login"] = login
    return render_template(template, **context)

# Ensure session_id exists
@app.before_request
def ensure_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

def get_category_list():
    """
    [
        {
            "id"
            "name"
            "description"
        }
    ]
    """
    response = requests.get(f"http://product:5000/api/categories")
    response.raise_for_status()  # Raise error if request failed
    data = response.json()
    return data

@app.route("/")
def index():
    category_list = get_category_list()
    return render_template_base("index.html", category_list=category_list)

def get_user(user_id):
    """
    {
        "id"
        "username"
        "realname"
        "email"
    }
    """
    response = requests.get(f"http://user:5000/api/users/{user_id}")
    response.raise_for_status()  
    data = response.json()
    return data

def get_user_orders(user_id):
    """
    [
        {
            "id"
            "user_id"
            "time"
            "total_price_in_cents"
            "address_name"
            "address1"
            "address2"
            "credit_card_company"
            "credit_card_number"
            "credit_card_expiry"
        }
    ]
    """
    response = requests.get(f"http://order:5000/api/orders/{user_id}")
    response.raise_for_status() 
    data = response.json()
    return data

@app.route("/profile")
def profile():

    login = "user_id" in session
    if not login:
        flash("You are not signed in.")
        response = make_response(redirect("/login"))
        response.headers["Referer"] = "/profile"
        return response

    category_list = get_category_list()

    user_id = session.get("user_id")
    user = get_user(user_id)
    orders: list[dict] = get_user_orders(user_id)
    for order in orders:
        # get shipping status
        ship_resp = requests.get(f"http://shipping:5000/api/shipping/status/{order.get('shipping_id')}")
        ship_data = ship_resp.json()
        status = ship_data.get("status")
        order.update({"status": status})

    return render_template_base("profile.html", category_list=category_list, user=user, orders=orders)

def call_login(username, password):
    data = {
        "username": username,
        "password": password
    }

    response = requests.post("http://user:5000/api/users/login", json=data)
    data = response.json()

    if response.status_code == 200:
        session["user_id"] = data.get("user_id")

        data = {
            "old_id": "temp:"+session.get("session_id"),
            "new_id": data.get("user_id")
        }
        response = requests.post("http://cart:5000/api/cart/upgrade", json=data)
        return True
    else:
        return False

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        referer = request.form.get("referer", None)
        if call_login(username, password):
            if referer:
                return redirect(referer)
            return redirect("/")
        else:
            flash('Invalid credentials. Please try again.')
            return render_template_base("login.html")
    
    if "user_id" in session:
        flash("You are already logged in. Please sign out before logging in.")
        return redirect("/")

    category_list = get_category_list()
    referer = request.referrer
    return render_template_base("login.html", referer=referer, category_list=category_list)

def call_logout():
    session.pop("session_id")
    session.pop("user_id")
    return True

@app.route("/logout")
def logout():
    if call_logout():
        flash("You have been logged out.")
        return redirect("/")
    
    flash("Logout failed.")
    return redirect("/")

def get_category(category_id):
    response = requests.get(f"http://product:5000/api/categories/{category_id}")
    response.raise_for_status()

    data = response.json()
    return data

def get_products_for_category(category_id):
    response = requests.get(f"http://product:5000/api/categories/{category_id}/products")
    response.raise_for_status()

    data = response.json()
    return data

@app.route("/category", methods=['GET', 'POST'])
def category():
    if request.method == 'POST':
        selected_number_of_products = request.form['number']
        session["selected_number_of_products"] = selected_number_of_products

    product_number_options = [1, 2, 3, 4, 5]
    page = request.args.get('page', default=1, type=int)
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

    images = get_images([p.get("img_name") for p in products_page])
    for p in products_page:
        p["image"] = images.get(p.get("img_name"))

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

def get_product(product_id):
    response = requests.get(f"http://product:5000/api/products/{product_id}")
    response.raise_for_status()

    data = response.json()
    return data

def get_products(product_ids):
    products = []

    for id in product_ids:
        products.append(get_product(id))
    
    return products

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
    image = get_image(product.get("img_name"))
    product["image"] = image

    ads_ids = get_recommendations()
    ads = get_products(ads_ids)
    ad_images = get_images([p.get("img_name") for p in ads])
    for p in ads:
        p["image"] = ad_images[p.get("img_name")]

    category_list = get_category_list()
    return render_template_base("product.html", category_list=category_list, product=product, ads=ads)

@app.route("/cart")
def cart():
    id = session.get("user_id") if "user_id" in session else "temp:"+session.get("session_id")
    response = requests.get(f"http://cart:5000/api/cart/{id}")
    response.raise_for_status()
    cart_items = response.json()

    products = get_products([i.get("product_id") for i in cart_items])
    products_map = {
        int(p.get("id")) : p for p in products
    }

    ads_ids = get_recommendations()
    ads = get_products(ads_ids)
    ad_images = get_images([p.get("img_name") for p in ads])
    for p in ads:
        image = ad_images[p.get("img_name")]
        p.update({"image": image})

    category_list = get_category_list()
    return render_template_base("cart.html", category_list=category_list, products=products_map, ads=ads, order_items=cart_items)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("productid", type=int)
    id = session.get("user_id") if "user_id" in session else "temp:"+session.get("session_id")
    data = {
        "product_id": product_id,
        "id": id
    }
    response = requests.post("http://cart:5000/api/cart/add", json=data)
    if response.status_code == 200:
        flash("Product added to cart.")
        return redirect("/cart")
    else:
        flash("Failed to add product to cart.")
        return redirect("/cart")

@app.route("/update-cart", methods=["POST"])
def update_cart():
    id = session.get("user_id") if "user_id" in session else "temp:"+session.get("session_id")
    # remove item
    product_to_remove = request.form.get("remove_item")
    if product_to_remove:
        data = {
            "product_id": product_to_remove,
            "id": id
        }
        response = requests.post("http://cart:5000/api/cart/remove", json=data)
        if response.status_code == 200:
            flash("Product removed from cart.")
            return redirect("/cart")
        else:
            flash("Failed to remove product from cart.")
            return redirect("/cart")

    # update cart
    all_items = {}
    for key, val in request.form.items():
        if key.startswith("quantity_"):
            product_id = key.strip("quantity_")
            all_items[product_id] = int(val)
    data = {
        "cart_items": all_items,
        "id": id
    }
    response = requests.post("http://cart:5000/api/cart/update", json=data)
    if response.status_code == 200:
        flash("Cart updated.")
        return redirect("/cart")
    
    else:
        flash("Failed to update cart.")
        return redirect("/cart")
    
@app.route("/checkout", methods=["POST"])
def checkout():
    if not "user_id" in session:
        response = make_response(redirect("/login"))
        response.headers["Referer"] = "/order"
        return response

    return redirect("/order")

@app.route("/order")
def order():
    id = session.get("user_id") if "user_id" in session else "temp:"+session.get("session_id")
    response = requests.get(f"http://cart:5000/api/cart/{id}")
    response.raise_for_status()
    cart_items = response.json()

    if not cart_items:
        flash("You have no items in your cart.")
        return redirect("/")

    return render_template_base("order.html")

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
    user_id = session.get("user_id")

    data = {
        "order": {
            "address_name": firstname + " " + lastname,
            "address1": address1,
            "address2": address2,
            "credit_card_company": cardtype,
            "credit_card_number": cardnumber,
            "credit_card_expiry": expirydate
        },
        "user_id": user_id
    }

    response = requests.post("http://order:5000/api/orders", json=data)
    data = response.json()
    if response.status_code == 200:
        return redirect("/")
    else:
        flash(f"Failed to confirm.\n{data.get('error')}")
        return redirect("/cart")
