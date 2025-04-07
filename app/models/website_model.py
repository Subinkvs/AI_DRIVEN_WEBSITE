from datetime import datetime

def get_website_document(user_email, business_type, industry, content):
    return {
        "user_email": user_email,
        "business_type": business_type,
        "industry": industry,
        "content": content,  # AI-generated HTML or text blocks
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_published": False,
        "customizations": {
            "images": [],
            "layout": "default",
            "sections": []  # Will hold user-edited content later
        }
    }
