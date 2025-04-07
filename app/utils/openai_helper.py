import os
import json
from openai import OpenAI

# Initialize OpenAI client using the new SDK
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_site_content(business_type, industry):
    prompt = f"""
    Generate structured website content for:
    Business Type: {business_type}
    Industry: {industry}

    Return in JSON:
    {{
        "title": "...",
        "hero": {{
            "headline": "...",
            "subheadline": "..."
        }},
        "about": "...",
        "services": ["...", "...", "..."],
        "contact": "..."
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4",  # You can change this to gpt-3.5-turbo if needed
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.7,
    )

    # Extract the content from the response
    return response.choices[0].message.content
