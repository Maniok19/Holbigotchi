from app.models.base import BaseModel
from app import db, bcrypt
import re

class User(BaseModel):
    """Modèle utilisateur pour les étudiants Holberton"""
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    cohort = db.Column(db.String(50), nullable=False)
    
    # Relation avec la cohorte (many-to-one)
    cohort_id = db.Column(db.Integer, db.ForeignKey('cohorts.id'), nullable=True)
    
    def __init__(self, email, username, password, cohort, cohort_id=None):
        """Initialise un nouvel utilisateur"""
        if not self.validate_email(email):
            raise ValueError("L'email doit se terminer par @holbertonstudents.com")
        
        if not self.validate_username(username):
            raise ValueError("Le nom d'utilisateur doit contenir entre 3 et 50 caractères et ne peut contenir que des lettres, chiffres et underscores")
        
        self.email = email
        self.username = username
        self.set_password(password)
        self.cohort = cohort
        self.cohort_id = cohort_id
    
    @staticmethod
    def validate_email(email):
        """Valide que l'email se termine par @holbertonstudents.com"""
        if not email or not isinstance(email, str):
            return False
        return email.endswith('@holbertonstudents.com')
    
    @staticmethod
    def validate_username(username):
        """Valide le nom d'utilisateur (3-50 caractères, lettres, chiffres, underscores)"""
        if not username or not isinstance(username, str):
            return False
        if len(username) < 3 or len(username) > 50:
            return False
        # Permet seulement lettres, chiffres et underscores
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
    
    def set_password(self, password):
        """Hache et stocke le mot de passe"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire (sans le mot de passe)"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'cohort': self.cohort,
            'cohort_id': self.cohort_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.email})>'