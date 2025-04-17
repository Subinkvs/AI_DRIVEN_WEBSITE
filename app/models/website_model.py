from datetime import datetime

def get_website_document(user_id, business_type, industry, content):
    """
    Generate a website document dictionary with metadata for storage.

    Args:
        user_id (str or int): The unique identifier of the user creating the website.
        business_type (str): The type of business the website represents.
        industry (str): The industry the business operates in.
        content (dict): The website content, including AI-generated sections.

    Returns:
        dict: A dictionary representing the website document, including timestamps and publication status.
    """ 
    return {
        "user_id": user_id,
        "business_type": business_type,
        "industry": industry,
        "content": content,  # includes sections (AI-generated)
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_published": False,
    }
