import os

class Config:
    MONGO_URI = "mongodb://localhost:27017/AI_DB"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Use a secret key stored in env variable
    JWT_TOKEN_LOCATION = ["headers"]  # <-- Important!
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"  # default, optional
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
