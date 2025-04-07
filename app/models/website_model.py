from datetime import datetime

def get_website_document(user_id, business_type, industry, content):
    return {
        "user_id": user_id,
        "business_type": business_type,
        "industry": industry,
        "content": content,  # includes sections (AI-generated)
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_published": False,
        "customizations": {
            "images": [],
            "layout": "default"
        }
    }
