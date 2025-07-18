from app.models.user import User
from app.models.cohort import Cohort
from app.models.holbigotchi import Holbigotchi
from app.persistence.repository import SQLAlchemyRepository
from app import db

class UserFacade:
    def __init__(self):
        self.repository = SQLAlchemyRepository(User)

    def create_user(self, email, username, password, cohort):
        user = User(email=email, username=username, password=password, cohort=cohort)
        db.session.add(user)
        db.session.commit()
        return user

    def get_user_by_email(self, email):
        return self.repository.get_by_attribute('email', email)

    def get_user_by_username(self, username):
        return self.repository.get_by_attribute('username', username)

    def get_user(self, user_id):
        return self.repository.get(user_id)

    def update_user(self, user_id, **kwargs):
        user = self.get_user(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            db.session.commit()
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            self.repository.delete(user_id)
            return True
        return False

class CohortFacade:
    def __init__(self):
        self.repository = SQLAlchemyRepository(Cohort)

    def create_cohort(self, name, description=None):
        cohort = Cohort(name=name, description=description)
        db.session.add(cohort)
        db.session.commit()
        
        # Créer automatiquement un Holbigotchi pour cette cohorte
        holbigotchi = Holbigotchi(cohort_id=cohort.id)
        db.session.add(holbigotchi)
        db.session.commit()
        
        return cohort

    def get_cohort(self, cohort_id):
        return self.repository.get(cohort_id)

    def get_all_cohorts(self):
        return self.repository.get_all()

    def update_cohort(self, cohort_id, **kwargs):
        cohort = self.get_cohort(cohort_id)
        if cohort:
            for key, value in kwargs.items():
                setattr(cohort, key, value)
            db.session.commit()
            return cohort
        return None

    def delete_cohort(self, cohort_id):
        cohort = self.get_cohort(cohort_id)
        if cohort:
            # Supprimer le Holbigotchi associé
            if cohort.holbigotchi:
                db.session.delete(cohort.holbigotchi)
            self.repository.delete(cohort_id)
            return True
        return False

class HolbigotchiFacade:
    def __init__(self):
        self.repository = SQLAlchemyRepository(Holbigotchi)

    def create_holbigotchi(self, cohort_id, health_points=70, evolution_state='egg'):
        holbigotchi = Holbigotchi(cohort_id=cohort_id, health_points=health_points, evolution_state=evolution_state)
        db.session.add(holbigotchi)
        db.session.commit()
        return holbigotchi

    def get_holbigotchi(self, holbigotchi_id):
        return self.repository.get(holbigotchi_id)

    def get_holbigotchi_by_cohort(self, cohort_id):
        return self.repository.get_by_attribute('cohort_id', cohort_id)

    def get_all_holbigotchi(self):
        return self.repository.get_all()

    def feed_holbigotchi(self, holbigotchi_id, health_boost=10):
        holbigotchi = self.get_holbigotchi(holbigotchi_id)
        if holbigotchi:
            holbigotchi.feed(health_boost)
            return holbigotchi
        return None

    def evolve_holbigotchi(self, holbigotchi_id):
        holbigotchi = self.get_holbigotchi(holbigotchi_id)
        if holbigotchi:
            return holbigotchi.evolve()
        return False

    def update_health(self, holbigotchi_id, health_change):
        holbigotchi = self.get_holbigotchi(holbigotchi_id)
        if holbigotchi:
            if health_change > 0:
                holbigotchi.health_points = min(100, holbigotchi.health_points + health_change)
            else:
                holbigotchi.decay_health(abs(health_change))
            return holbigotchi
        return None

# Instances globales
user_facade = UserFacade()
cohort_facade = CohortFacade()
holbigotchi_facade = HolbigotchiFacade()