from app.models.base import BaseModel
from app import db, bcrypt
import re

class User(BaseModel):
    """Modèle utilisateur pour les étudiants Holberton"""
    __tablename__ = 'users'
    
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    cohort = db.Column(db.String(50), nullable=False)
    
    # Relation avec la cohorte (many-to-one)
    cohort_id = db.Column(db.Integer, db.ForeignKey('cohorts.id'), nullable=True)
    
    def __init__(self, email, password, cohort, cohort_id=None):
        """Initialise un nouvel utilisateur"""
        if not self.validate_email(email):
            raise ValueError("L'email doit se terminer par @holbertonstudents.com")
        
        self.email = email
        self.set_password(password)
        self.cohort = cohort
        self.cohort_id = cohort_id
    
    @staticmethod
    def validate_email(email):
        """Valide que l'email se termine par @holbertonstudents.com"""
        if not email or not isinstance(email, str):
            return False
        return email.endswith('@holbertonstudents.com')
    
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
            'cohort': self.cohort,
            'cohort_id': self.cohort_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.email}>'