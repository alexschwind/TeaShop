from flask import Flask, request, jsonify, abort

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
            "realname": self.realname,
            "email": self.email
        }

users = [
    User(1, "alice", "pass123", "Alice Smith", "alice@example.com"),
    User(2, "bob", "secret", "Bob Jones", "bob@example.com"),
    User(3, "user2", "password", "Testuser", "test@email.com")
]

def find_by_id(items, id):
    return next((item for item in items if item.id == id), None)

def next_id(items):
    return max((item.id for item in items), default=0) + 1

app = Flask(__name__)

@app.route("/api/users/login", methods=["POST"])
def login():

    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = next((u for u in users if u.username == username), None)
    if user:
        if password == user.password:
            return jsonify({
                "success": "user is correct",
                "user_id": user.id
            })
        else:
            return jsonify({
                "error": "user is not correct"
            })
    abort(404)

@app.route("/api/users/<int:id>", methods=["GET"])
def get_user(id):
    user = find_by_id(users, id)
    if user:
        return jsonify(user.to_dict())
    abort(404)