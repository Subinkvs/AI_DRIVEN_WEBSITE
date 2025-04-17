from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from app.config import Config
from .extensions import limiter
from .extensions import cache

mongo = PyMongo()
jwt = JWTManager()

def create_app():
    """
    Create and configure the Flask application.

    This function initializes the Flask app with configuration settings,
    sets up MongoDB via PyMongo, JWT authentication, rate limiting, and caching.
    It also registers blueprints for authentication and website routes.

    Returns:
        Flask: The configured Flask application instance.
    """

    app = Flask(
        __name__,
        static_folder='static',
        static_url_path='/static'
    )
    app.config.from_object(Config)

    mongo.init_app(app)
    jwt.init_app(app)
    
    # Initialize extensions
    limiter.init_app(app)
    
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    cache.init_app(app)


    from app.routes.auth_routes import auth_bp
    from app.routes.website_routes import website_bp  # ✅ Add this

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(website_bp, url_prefix="/website")  # ✅ Register website API
    
    return app


