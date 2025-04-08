from flask import Blueprint, request, jsonify,redirect
from app import mongo
from app.models.user_model import UserModel
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"message": "Missing name, email, or password"}), 400

        if UserModel.find_by_email(mongo.db, email):
            return jsonify({"message": "User already exists"}), 409

        UserModel.create_user(mongo.db, name, email, password)

        return jsonify({"message": "Registration successful. You can now log in."}), 201


    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400

        user = UserModel.find_by_email(mongo.db, email)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if not UserModel.verify_password(user, password):
            return jsonify({"message": "Invalid password"}), 401

        access_token = create_access_token(
            identity=email,
            expires_delta=timedelta(days=1)
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

