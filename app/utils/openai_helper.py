import os
import re
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image(prompt):
    """
    Generate an image using OpenAI's DALL·E 3 model based on a given text prompt.

    Args:
        prompt (str): A descriptive text prompt to generate the image.

    Returns:
        str: The URL of the generated image.
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

def extract_json(text):
    """Extracts and returns the first valid JSON object from a string."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No valid JSON found in the response.")

def generate_site_content(business_type, industry):
    prompt = f"""
    You are a web content generator. Return ONLY a valid JSON object with the following structure.
    Do not include markdown, explanations, or extra text.

    Business Type: {business_type}
    Industry: {industry}

    {{
        "title": "string",
        "sections": [
            {{
                "title": "Hero Section",
                "type": "hero",
                "body": {{
                    "headline": "string",
                    "subheadline": "string"
                }}
            }},
            {{
                "title": "About Us",
                "type": "about",
                "body": "string"
            }},
            {{
                "title": "Services",
                "type": "services",
                "body": ["string", "string", "string"]
            }},
            {{
                "title": "Contact",
                "type": "contact",
                "body": "string"
            }}
        ]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.7,
    )

    raw_text = response.choices[0].message.content.strip()
    content_json = extract_json(raw_text)

    # Generate images for each section
    for section in content_json.get("sections", []):
        section_type = section["type"]

        if section_type == "hero":
            section["image_url"] = generate_image(f"Banner for a {business_type} in {industry}")
        
        elif section_type == "about":
            section["image_url"] = generate_image(f"About us image for a {business_type} in {industry}")
        
        elif section_type == "services":
            service_images = []
            for idx, service in enumerate(section["body"]):
                img = generate_image(f"Image representing '{service}' service in {industry} industry for a {business_type}")
                service_images.append(img)
            section["image_urls"] = service_images  # note: plural 'image_urls' for list
        
        elif section_type == "contact":
            section["image_url"] = generate_image(f"Contact page image for a {business_type} in {industry}")

    return content_json



