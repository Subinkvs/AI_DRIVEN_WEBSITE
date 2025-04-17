import os

class Config:
    """
    Configuration class for the Flask application.

    This class holds all necessary configuration variables such as
    MongoDB URI, JWT settings, and the OpenAI API key. It uses environment
    variables when available to ensure sensitive data is not hardcoded.

    Attributes:
        MONGO_URI (str): MongoDB connection string.
        JWT_SECRET_KEY (str): Secret key used to encode JWT tokens.
        JWT_TOKEN_LOCATION (list): Where to look for JWTs in incoming requests.
        JWT_HEADER_NAME (str): The header name used to pass JWT.
        JWT_HEADER_TYPE (str): Prefix used before the JWT in headers.
        OPENAI_API_KEY (str): API key for accessing OpenAI services.
    """
    
    MONGO_URI = "mongodb://localhost:27017/AI_DB"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Use a secret key stored in env variable
    JWT_TOKEN_LOCATION = ["headers"]  # <-- Important!
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"  # default, optional
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
