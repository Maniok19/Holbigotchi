from app.models.base import BaseModel
from app import db

class Cohort(BaseModel):
    """Modèle représentant une cohorte d'étudiants"""
    __tablename__ = 'cohorts'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relation one-to-one avec Holbigotchi
    holbigotchi = db.relationship('Holbigotchi', back_populates='cohort', uselist=False)
    
    # Relation one-to-many avec les utilisateurs
    users = db.relationship('User', backref='cohort_relation', lazy=True)
    
    def __init__(self, name, description=None):
        """Initialise une nouvelle cohorte"""
        self.name = name
        self.description = description
    
    def to_dict(self):
        """Convertit la cohorte en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Cohort {self.name}>'