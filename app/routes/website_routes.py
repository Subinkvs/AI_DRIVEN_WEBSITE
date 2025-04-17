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
def profile_api():
    user_id = get_jwt_identity()
    websites = list(mongo.db.websites.find({"user_id": user_id}))
    
    for site in websites:
        site["_id"] = str(site["_id"])

    return jsonify({"websites": websites})


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


from bson.errors import InvalidId

@website_bp.route("/<website_id>/content", methods=["PATCH"])
@jwt_required()
@limiter.limit("100 per minute")
def patch_website_content(website_id):
    """
    Update the content sections of a website document by its ID.

    This route requires user authentication and is rate-limited to 100 requests per minute.

    The authenticated user must be the owner of the website. The content's sections will be updated
    based on the `type` of each section. If a section of the same `type` already exists, it will be updated;
    otherwise, the new section will be added. Layout and title updates are also supported.

    Args:
        website_id (str): The string representation of the website's ObjectId.

    Request Body (JSON):
        {
            "sections": [  # list of section objects
                {
                    "type": "header",
                    "content": "Updated content"
                },
                ...
            ],
            "layout": "new-layout-name",
            "title": "Updated Website Title"
        }

    Returns:
        Response:
            - 200 OK with success message on successful update.
            - 400 Bad Request if the website ID is invalid or no content is provided.
            - 404 Not Found if the website does not exist or user is unauthorized.
            - 500 Internal Server Error if an unexpected error occurs.
    """
    try:
        try:
            object_id = ObjectId(website_id)
        except InvalidId:
            return jsonify({"error": "Invalid website ID"}), 400

        data = request.get_json()
        user_id = get_jwt_identity()

        if not data:
            return jsonify({"error": "No content provided"}), 400

        website = mongo.db.websites.find_one(
            {"_id": object_id, "user_id": user_id}
        )
        if not website:
            return jsonify({"error": "Website not found or unauthorized"}), 404

        content = website.get("content", {})
        new_sections = data.get("sections", [])
        updated_sections = []

        for new_section in new_sections:
            section_type = new_section.get("type")
            if not section_type:
                continue

            # Try to find the existing section with the same type
            existing_section = next((s for s in content.get("sections", []) if s.get("type") == section_type), None)

            if existing_section:
                # Update existing section
                existing_section.update(new_section)
                updated_sections.append(existing_section)
            else:
                # Add new section
                updated_sections.append(new_section)

        content["sections"] = updated_sections
        content["layout"] = data.get("layout", content.get("layout", "default"))
        content["title"] = data.get("title", content.get("title", ""))

        mongo.db.websites.update_one(
            {"_id": object_id},
            {"$set": {"content": content, "updated_at": datetime.utcnow()}}
        )

        return jsonify({"message": "Content updated successfully"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An error occurred while updating content.",
            "details": str(e)
        }), 500





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
        
        
@website_bp.route("/websitecontent/<website_id>")
@jwt_required(optional=True)
def view_website(website_id):
    """
    Render a preview of the website content by website ID.

    This route is accessible with or without a valid JWT token.
    It attempts to fetch the website document from the database using the provided ID,
    and if found, renders the "preview.html" template with the website's content.

    Args:
        website_id (str): The string representation of the website's ObjectId.

    Returns:
        Response: 
            - Renders "preview.html" with the website content if found.
            - Returns a 400 error if the ID is invalid.
            - Returns a 404 error if the website is not found in the database.
    """
    try:
        object_id = ObjectId(website_id)
    except InvalidId:
        return "Invalid website ID", 400

    website = mongo.db.websites.find_one({"_id": object_id})
    if not website:
        return "Website not found", 404

    content = website.get("content", {})

    return render_template("preview.html", content=content)


