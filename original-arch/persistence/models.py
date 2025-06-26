class User:
    def __init__(self, id: int, username: str, password: str, realname: str, email: str):
        self.id = int(id)
        self.username = username
        self.password = password
        self.realname = realname
        self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "realname": self.realname,
            "email": self.email
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
                 address1: str, address2: str, credit_card_company: str, credit_card_number: str, credit_card_expiry: str):
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
        }
    
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