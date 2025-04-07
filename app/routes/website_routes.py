from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.openai_helper import generate_site_content
from app import mongo
import json
from datetime import datetime

website_bp = Blueprint("website", __name__)


@website_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_website():
    data = request.get_json()
    business_type = data.get("business_type")
    industry = data.get("industry")

    if not business_type or not industry:
        return jsonify({"error": "Missing fields"}), 400

    try:
        user_id = get_jwt_identity()
        content = generate_site_content(business_type, industry)

        website_doc = {
            "user_id": user_id,
            "business_type": business_type,
            "industry": industry,
            "content": json.loads(content),
            "created_at": datetime.utcnow()
        }

        result = mongo.db.websites.insert_one(website_doc)

        return jsonify({
            "message": "Website generated",
            "website_id": str(result.inserted_id),
            "content": website_doc["content"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
