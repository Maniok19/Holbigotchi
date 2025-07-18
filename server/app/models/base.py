from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class BaseModel(db.Model):
    """Modèle de base avec des champs communs"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Sauvegarde l'objet en base"""
        db.session.add(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Met à jour les attributs de l'objet"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        """Supprime l'objet de la base"""
        db.session.delete(self)
        db.session.commit()