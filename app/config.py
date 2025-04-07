import os

class Config:
    MONGO_URI = "mongodb://localhost:27017/AI_DB"
    JWT_SECRET_KEY = "your-secret-key"  # Replace with a secure key in production
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
