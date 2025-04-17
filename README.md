# 🌐 AI Website Generator API

This Flask-based REST API allows authenticated users to generate, retrieve, update, and delete AI-generated website content. It uses JWT for authentication and stores data in MongoDB.

## 🚀 Features

- Generate AI-powered website content based on business type and industry
- Retrieve individual or all websites for a user
- Update or patch website content
- Delete websites
- Rate limiting & caching support
- JWT-based user authentication

## 🛠️ Tech Stack

- Python + Flask
- Javascript
- MongoDB (via PyMongo)
- Flask-JWT-Extended
- Flask-Caching
- Flask-Limiter
- OpenAI (for content generation)

---

## 🔐 Authentication

All endpoints require a valid **JWT access token** in the `Authorization` header:


## Installations 
```sh
git clone https://github.com/Subinkvs/AI_DRIVEN_WEBSITE.git
```

```sh
pip install -r requirements.txt
```
## Set Environment Variables for OPENAI_API KEY

Create a `.env` file in the root directory and add the following:

```sh
OPENAI_API_KEY = ""
```
## Set MongoDB connection

In config.py
```sh
 MONGO_URI = "mongodb://localhost:27017/DATABASE_NAME"
```
## Run in local server
```sh
python run.py
```


