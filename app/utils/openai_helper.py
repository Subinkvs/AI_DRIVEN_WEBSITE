import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_site_content(business_type, industry):
    prompt = f"""
    Generate structured website content for:
    Business Type: {business_type}
    Industry: {industry}

    Return in JSON:
    {{
        "title": "...",
        "sections": [
            {{
                "title": "Hero Section",
                "type": "hero",
                "body": {{
                    "headline": "...",
                    "subheadline": "..."
                }},
                "images": ["hero1.jpg"]
            }},
            {{
                "title": "About Us",
                "type": "about",
                "body": "...",
                "images": []
            }},
            {{
                "title": "Services",
                "type": "services",
                "body": ["Service 1", "Service 2", "Service 3"],
                "images": []
            }},
            {{
                "title": "Contact",
                "type": "contact",
                "body": "...",
                "images": []
            }}
        ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7,
    )

    content_json = response.choices[0].message.content.strip()

    import json
    return json.loads(content_json)  # Return as dict

