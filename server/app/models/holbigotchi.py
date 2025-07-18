import random
from app.models.base import BaseModel
from app import db
from datetime import datetime

class Holbigotchi(BaseModel):
    """Modèle représentant un Holbigotchi virtuel pour une cohorte"""
    __tablename__ = 'holbigotchis'
    
    # Relation avec la cohorte (one-to-one)
    cohort_id = db.Column(db.Integer, db.ForeignKey('cohorts.id'), nullable=False, unique=True)
    cohort = db.relationship('Cohort', back_populates='holbigotchi')
    
    # Statistiques du Holbigotchi
    health_points = db.Column(db.Integer, nullable=False, default=70)
    last_feed_at = db.Column(db.DateTime, nullable=True)
    evolution_state = db.Column(db.String(20), nullable=False, default='egg')
    
    # Asset 3D associé au Holbigotchi
    asset_folder = db.Column(db.String(100), nullable=False, default='Guecko')
    
    # Liste des assets disponibles
    AVAILABLE_ASSETS = {
        'Guecko': {
            'model_gltf': 'Gecko.gltf',
            'model_bin': 'Gecko.bin',
            'texture': 'T_Gecko.png'
        },
        'Monkey': {
            'model_gltf': 'Colobus.gltf',
            'model_bin': 'Colobus.bin',
            'texture': 'T_Colobus.png'
        },
        'moskrat': {
            'model_gltf': 'Muskrat.gltf',
            'model_bin': 'Muskrat.bin',
            'texture': 'T_Muskrat.png'
        },
        'dog_bowl': {
            'model_gltf': 'DogBowlFBX.gltf',
            'model_bin': 'DogBowlFBX.bin',
            'texture': 'DogBowl01_DogBowl01_BaseColor.jpg'
        }
    }
    
    # Contraintes pour health_points (0-100)
    __table_args__ = (
        db.CheckConstraint('health_points >= 0 AND health_points <= 100', 
                         name='check_health_points_range'),
    )
    
    def __init__(self, cohort_id, health_points=70, evolution_state='egg', asset_folder=None):
        """Initialise un nouveau Holbigotchi"""
        self.cohort_id = cohort_id
        self.health_points = max(0, min(100, health_points))
        self.evolution_state = evolution_state
        
        # Assigner un asset aléatoire si aucun n'est spécifié
        if asset_folder is None:
            asset_folder = self.assign_random_asset()
        
        self.asset_folder = asset_folder
        self.last_feed_at = None
    
    @classmethod
    def assign_random_asset(cls):
        """Assigne un asset aléatoire parmi ceux disponibles"""
        return random.choice(list(cls.AVAILABLE_ASSETS.keys()))
    
    @classmethod
    def get_available_assets(cls):
        """Retourne la liste des assets disponibles"""
        return list(cls.AVAILABLE_ASSETS.keys())
    
    def get_asset_paths(self):
        """
        Retourne les chemins vers les assets 3D du Holbigotchi
        
        Returns:
            dict: Dictionnaire avec les chemins vers les différents assets
        """
        if self.asset_folder not in self.AVAILABLE_ASSETS:
            # Asset par défaut si l'asset n'existe pas
            self.asset_folder = 'Guecko'
        
        asset_config = self.AVAILABLE_ASSETS[self.asset_folder]
        base_path = f"/assets/{self.asset_folder}"
        
        return {
            'model_gltf': f"{base_path}/{asset_config['model_gltf']}",
            'model_bin': f"{base_path}/{asset_config['model_bin']}",
            'texture': f"{base_path}/{asset_config['texture']}"
        }
    
    def get_status(self):
        """
        Retourne le statut de santé du Holbigotchi
        
        Returns:
            str: "healthy", "sick", ou "dead"
        """
        if self.health_points >= 70:
            return "healthy"
        elif self.health_points >= 30:
            return "sick"
        else:
            return "dead"
    
    def feed(self, health_boost=10):
        """
        Nourrit le Holbigotchi et met à jour ses statistiques
        
        Args:
            health_boost (int): Points de santé à ajouter (défaut: 10)
        """
        self.health_points = min(100, self.health_points + health_boost)
        self.last_feed_at = datetime.utcnow()
        db.session.commit()
    
    def decay_health(self, decay_amount=5):
        """
        Diminue la santé du Holbigotchi (appelé périodiquement)
        
        Args:
            decay_amount (int): Points de santé à retirer (défaut: 5)
        """
        self.health_points = max(0, self.health_points - decay_amount)
        db.session.commit()
    
    def can_evolve(self):
        """
        Vérifie si le Holbigotchi peut évoluer
        
        Returns:
            bool: True si l'évolution est possible
        """
        # Critères d'évolution basés sur la santé et le temps
        if self.evolution_state == 'egg' and self.health_points >= 80:
            return True
        elif self.evolution_state == 'baby' and self.health_points >= 90:
            return True
        return False
    
    def evolve(self):
        """
        Fait évoluer le Holbigotchi vers le stade suivant
        
        Returns:
            bool: True si l'évolution a eu lieu
        """
        if not self.can_evolve():
            return False
        
        if self.evolution_state == 'egg':
            self.evolution_state = 'baby'
        elif self.evolution_state == 'baby':
            self.evolution_state = 'adult'
        else:
            return False  # Déjà au stade adulte
        
        db.session.commit()
        return True
    
    def days_since_last_feed(self):
        """
        Calcule le nombre de jours depuis la dernière alimentation
        
        Returns:
            int: Nombre de jours (0 si jamais nourri)
        """
        if not self.last_feed_at:
            return 0
        
        delta = datetime.utcnow() - self.last_feed_at
        return delta.days
    
    def to_dict(self):
        """Convertit le Holbigotchi en dictionnaire"""
        return {
            'id': self.id,
            'cohort_id': self.cohort_id,
            'health_points': self.health_points,
            'last_feed_at': self.last_feed_at.isoformat() if self.last_feed_at else None,
            'evolution_state': self.evolution_state,
            'status': self.get_status(),
            'days_since_last_feed': self.days_since_last_feed(),
            'can_evolve': self.can_evolve(),
            'asset_folder': self.asset_folder,
            'asset_paths': self.get_asset_paths(),
            'available_assets': self.get_available_assets(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Holbigotchi {self.evolution_state} - HP: {self.health_points} - Asset: {self.asset_folder}>'