from flask import Blueprint, request, jsonify,redirect
from app import mongo
from app.models.user_model import UserModel
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    This endpoint allows a user to register by providing their name, email, and password.
    It checks if all required fields are provided and if the email is already registered.

    Request JSON:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword"
    }

    Returns:
        201 Created - If the registration is successful.
        400 Bad Request - If required fields are missing.
        409 Conflict - If the user with the given email already exists.
        500 Internal Server Error - If an unexpected error occurs.

    Example Response:
    {
        "message": "Registration successful. You can now log in."
    }
    """
    
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
    """
    Authenticate an existing user and return a JWT access token.

    This endpoint allows users to log in using their email and password.
    Upon successful authentication, a JWT access token valid for 1 day is returned.

    Request JSON:
    {
        "email": "john@example.com",
        "password": "securepassword"
    }

    Returns:
        200 OK - If login is successful with a JWT token.
        400 Bad Request - If email or password is missing.
        404 Not Found - If the user does not exist.
        401 Unauthorized - If the password is incorrect.
        500 Internal Server Error - If an unexpected error occurs.

    Example Response:
    {
        "message": "Login successful",
        "access_token": "<jwt-token>"
    }
    """
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
            "access_token": access_token,
            "user_name": user.get("name") 
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

