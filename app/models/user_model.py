from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UserModel:
    @staticmethod
    def find_by_email(db, email):
        return db.users.find_one({"email": email})

    @staticmethod
    def create_user(db, name, email, password):
        hashed_password = generate_password_hash(password)
        user = {
            "name": name,
            "email": email,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow()
        }
        db.users.insert_one(user)

    @staticmethod
    def verify_password(user_doc, password):
        return check_password_hash(user_doc["password_hash"], password)


