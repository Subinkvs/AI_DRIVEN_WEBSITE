from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/AI_DB"
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Replace with a strong secret in production
mongo = PyMongo(app)
jwt = JWTManager(app)
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/AI_DB"
app.config["JWT_SECRET_KEY"] = "your-secret-key"
mongo = PyMongo(app)
jwt = JWTManager(app)

@app.route("/register", methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({"message": "Missing name, email, or password"}), 400

        # Check if user already exists
        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            return jsonify({"message": "User already exists"}), 409

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert user into DB
        user = {
            "name": name,
            "email": email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow()
        }
        mongo.db.users.insert_one(user)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/login", methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400

        user = mongo.db.users.find_one({"email": email})
        if not user:
            return jsonify({"message": "User not found"}), 404

        if not check_password_hash(user['password_hash'], password):
            return jsonify({"message": "Invalid password"}), 401

        # Generate JWT access token (valid for 1 day)
        access_token = create_access_token(
            identity=str(user["email"]),
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


        

if __name__ == "__main__":
    app.run(debug=True)

