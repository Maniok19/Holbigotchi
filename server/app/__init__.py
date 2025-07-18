from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialisation des extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Configuration CORS - correction pour supporter les requêtes depuis le navigateur
    CORS(app, 
         origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    # Import des modèles (nécessaire pour db.create_all())
    from app.models import User, Cohort, Holbigotchi
    
    # Création des tables
    with app.app_context():
        db.create_all()
    
    # Enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.cohorts import cohorts_bp
    from app.routes.holbigotchi import holbigotchi_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(cohorts_bp, url_prefix='/api/v1/cohorts')
    app.register_blueprint(holbigotchi_bp, url_prefix='/api/v1/holbigotchi')
    
    return app