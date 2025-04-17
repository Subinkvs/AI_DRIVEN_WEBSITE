from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UserModel:
    @staticmethod
    def find_by_email(db, email):
        """
        Find a user document in the database by email.

        Args:
            db: The database connection object.
            email (str): The email address of the user to search for.

        Returns:
            dict or None: The user document if found, otherwise None.
        """
        return db.users.find_one({"email": email})

    @staticmethod
    def create_user(db, name, email, password):
        """
        Create a new user in the database with hashed password.

        Args:
            db: The database connection object.
            name (str): The name of the user.
            email (str): The email address of the user.
            password (str): The plaintext password of the user.

        Returns:
            None
        """
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
        """
        Verify a plaintext password against the stored hashed password.

        Args:
            user_doc (dict): The user document containing the hashed password.
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(user_doc["password_hash"], password)


