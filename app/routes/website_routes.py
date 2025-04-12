from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.openai_helper import generate_site_content
from app.models.website_model import get_website_document
from app import mongo
from datetime import datetime
from bson import ObjectId
from app.extensions import limiter
from app.extensions import cache

website_bp = Blueprint("website", __name__)


@website_bp.route("/generate", methods=["POST"])
@jwt_required()
@limiter.limit("100 per minute")
def generate_website():
    """
    Generate and store a new website for the authenticated user using AI-generated content.

    Request JSON Body:
        {
            "business_type": "string",
            "industry": "string"
        }

    This endpoint accepts business type and industry details from the user,
    invokes an AI content generation utility to produce structured website content,
    and stores it in the MongoDB collection under the authenticated user's account.

    Returns:
        JSON response containing a success message, the inserted website's ID,
        and the generated content.

    Status Codes:
        201 Created - Website successfully generated and stored.
        400 Bad Request - Missing required fields in request body.
        500 Internal Server Error - An unexpected error occurred during generation or insertion.
    """

    data = request.get_json()
    business_type = data.get("business_type")
    industry = data.get("industry")

    if not business_type or not industry:
        return jsonify({"error": "Missing fields"}), 400

    try:
        user_id = get_jwt_identity()
        content = generate_site_content(business_type, industry)

        website_doc = get_website_document(user_id, business_type, industry, content)

        result = mongo.db.websites.insert_one(website_doc)

        return (
            jsonify(
                {
                    "message": "Website generated successfully",
                    "website_id": str(result.inserted_id),
                    "content": website_doc["content"],
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@website_bp.route('/preview/<website_id>')
def preview_website(website_id):
    website = mongo.db.websites.find_one({"_id": ObjectId(website_id)})
    if not website:
        return "Website not found", 404

    content = website.get("content", {})
    return render_template("preview.html", content=content)


@website_bp.route("/profile", methods=["GET"])
def profile_page():
    return render_template("profile.html")


@website_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    websites = list(mongo.db.websites.find({"user_id": user_id}))

    for site in websites:
        site["_id"] = str(site["_id"])  # Convert ObjectId to string for Jinja

    return render_template("profile.html", websites=websites)




@website_bp.route("/<website_id>", methods=["GET"])
@jwt_required()
@limiter.limit("100 per minute")
@cache.cached(timeout=300)
def get_website_by_id(website_id):
    """
    Retrieve a specific website by its ID for the authenticated user.

    Args:
        website_id (str): The unique identifier of the website document in MongoDB.

    This endpoint fetches a website from the database if it exists and belongs to
    the currently authenticated user. The website ID must be a valid MongoDB ObjectId.

    Returns:
        JSON response containing the website data if found.
        404 error if the website does not exist or does not belong to the user.

    Status Codes:
        200 OK - Website found and returned successfully.
        404 Not Found - Website does not exist or access is denied.
        500 Internal Server Error - Unexpected error occurred.
    """
    try:
        user_id = get_jwt_identity()
        website = mongo.db.websites.find_one(
            {"_id": ObjectId(website_id), "user_id": user_id}
        )

        if not website:
            return jsonify({"error": "Website not found"}), 404

        website["_id"] = str(website["_id"])
        return jsonify(website), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "An error occurred while fetching the website.",
                    "details": str(e),
                }
            ),
            500,
        )


@website_bp.route("/user", methods=["GET"])
@jwt_required()
@limiter.limit("100 per minute")
@cache.cached(timeout=300)
def get_user_websites():
    """
    Get all websites created by the currently authenticated user.

    This endpoint retrieves all website documents from the database that are associated
    with the user identified by the JWT token. It ensures that users can only access
    their own websites.

    Returns:
        JSON response containing a list of the user's websites, each with its `_id`
        converted to a string.

    Status Codes:
        200 OK - Successful retrieval of websites.
        500 Internal Server Error - Unexpected error occurred.
    """
    try:
        user_id = get_jwt_identity()
        websites = mongo.db.websites.find({"user_id": user_id})

        result = []
        for site in websites:
            site["_id"] = str(site["_id"])
            result.append(site)

        return jsonify(result), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "An error occurred while fetching websites.",
                    "details": str(e),
                }
            ),
            500,
        )


@website_bp.route("/<website_id>", methods=["PUT"])
@jwt_required()
@limiter.limit("100 per minute")
def update_website(website_id):
    """
    Update a website by its ID for the authenticated user.

    This endpoint allows the user to update fields such as business_type, industry,
    content (e.g., text, images, layout), and customizations for a specific website.

    Args:
        website_id (str): The ID of the website document to be updated.

    Request Body (JSON):
        {
            "business_type": "Any business type",
            "industry": "Any industry",
            "content": {
                "title": "Custom Title",
                "sections": [
                    {
                        "title": "Section Title",
                        "type": "section_type",
                        "body": "...",
                        "images": [...]
                    },
                    ...
                ]
            },
            "customizations": {
                "layout": "custom_layout_name",
                "images": [...]
            }
        }

    Returns:
        200 OK: If the website is successfully updated.
        404 Not Found: If the website does not exist or does not belong to the user.
        500 Internal Server Error: For unexpected errors.
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        update_fields = {
            "business_type": data.get("business_type"),
            "industry": data.get("industry"),
            "content": data.get("content"),
            "customizations": data.get("customizations"),
            "updated_at": datetime.utcnow(),
        }

        result = mongo.db.websites.update_one(
            {"_id": ObjectId(website_id), "user_id": user_id}, {"$set": update_fields}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Website not found or unauthorized"}), 404

        return jsonify({"message": "Website updated"}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "An error occurred while updating the website.",
                    "details": str(e),
                }
            ),
            500,
        )


@website_bp.route("/<website_id>/content", methods=["PATCH"])
@jwt_required()
@limiter.limit("100 per minute")
def patch_website_content(website_id):
    """
    Partially updates the 'content' field of a website.

    URL: /<website_id>/content
    Method: PATCH
    Body: Partial content object (e.g., {'title': ..., 'sections': [...]})

    Returns:
        200 OK: If content is successfully updated.
        400 Bad Request: If no data is provided.
        404 Not Found: If the website does not exist or is unauthorized.
        500 Internal Server Error: For unexpected errors.
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        website = mongo.db.websites.find_one(
            {"_id": ObjectId(website_id), "user_id": user_id}
        )
        if not website:
            return jsonify({"error": "Website not found or unauthorized"}), 404

        # Update only the fields inside `content`
        content = website.get("content", {})
        content.update(data)

        # Apply the patch update
        mongo.db.websites.update_one(
            {"_id": ObjectId(website_id)},
            {"$set": {"content": content, "updated_at": datetime.utcnow()}},
        )

        return jsonify({"message": "Content updated successfully"}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "An error occurred while updating content.",
                    "details": str(e),
                }
            ),
            500,
        )


@website_bp.route("/<website_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("100 per minute")
def delete_website(website_id):
    """
    Deletes a website by its ID for the authenticated user.

    Method: DELETE
    URL: /<website_id>
    Authentication: JWT required

    Parameters:
        website_id (str): The unique ID of the website to delete (passed in the URL path).

    Returns:
        200 OK: If the website was successfully deleted.
        404 Not Found: If the website does not exist or does not belong to the authenticated user.
        500 Internal Server Error: For unexpected errors.
    """
    try:
        user_id = get_jwt_identity()
        result = mongo.db.websites.delete_one(
            {"_id": ObjectId(website_id), "user_id": user_id}
        )

        if result.deleted_count == 0:
            return jsonify({"error": "Website not found or unauthorized"}), 404

        return jsonify({"message": "Website deleted"}), 200

    except Exception as e:
        return (
            jsonify(
                {
                    "error": "An error occurred while deleting the website.",
                    "details": str(e),
                }
            ),
        )
