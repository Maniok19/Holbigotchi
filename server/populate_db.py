#!/usr/bin/env python3
"""
Script pour peupler la base de données avec des cohortes initiales
"""

from app import create_app, db
from app.models.cohort import Cohort
from app.models.holbigotchi import Holbigotchi
from app.models.user import User

def populate_cohorts():
    """Crée des cohortes de test avec des Holbigotchi ayant des assets variés"""
    
    # Cohortes par défaut avec assets spécifiques
    cohorts_data = [
        {
            'name': 'C20',
            'description': 'Cohorte 20 - Holberton School',
            'holbigotchi_asset': 'Guecko'
        },
        {
            'name': 'C21',
            'description': 'Cohorte 21 - Holberton School',
            'holbigotchi_asset': 'Monkey'
        },
        {
            'name': 'C22',
            'description': 'Cohorte 22 - Holberton School',
            'holbigotchi_asset': 'moskrat'
        },
        {
            'name': 'C23',
            'description': 'Cohorte 23 - Holberton School',
            'holbigotchi_asset': 'dog_bowl'
        },
        {
            'name': 'C24',
            'description': 'Cohorte 24 - Holberton School',
            'holbigotchi_asset': None  # Asset aléatoire
        },
        {
            'name': 'C25',
            'description': 'Cohorte 25 - Holberton School',
            'holbigotchi_asset': None  # Asset aléatoire
        },
        {
            'name': 'C26',
            'description': 'Cohorte 26 - Holberton School',
            'holbigotchi_asset': None  # Asset aléatoire
        }
    ]
    
    created_cohorts = []
    
    for cohort_data in cohorts_data:
        # Vérifier si la cohorte existe déjà
        existing_cohort = Cohort.query.filter_by(name=cohort_data['name']).first()
        
        if existing_cohort:
            print(f"✓ Cohorte {cohort_data['name']} existe déjà")
            
            # Vérifier si le Holbigotchi existe et mettre à jour son asset si nécessaire
            if existing_cohort.holbigotchi:
                holbi = existing_cohort.holbigotchi
                if cohort_data['holbigotchi_asset'] and holbi.asset_folder != cohort_data['holbigotchi_asset']:
                    old_asset = holbi.asset_folder
                    holbi.asset_folder = cohort_data['holbigotchi_asset']
                    db.session.commit()
                    print(f"  → Asset mis à jour: {old_asset} → {holbi.asset_folder}")
                else:
                    print(f"  → Holbigotchi avec asset: {holbi.asset_folder}")
            else:
                # Créer un Holbigotchi manquant
                holbigotchi = Holbigotchi(
                    cohort_id=existing_cohort.id,
                    asset_folder=cohort_data['holbigotchi_asset']
                )
                db.session.add(holbigotchi)
                db.session.commit()
                print(f"  → Holbigotchi créé avec asset: {holbigotchi.asset_folder}")
            
            created_cohorts.append(existing_cohort)
        else:
            # Créer la cohorte
            cohort = Cohort(
                name=cohort_data['name'],
                description=cohort_data['description']
            )
            
            try:
                db.session.add(cohort)
                db.session.commit()
                
                # Créer automatiquement un Holbigotchi pour cette cohorte
                holbigotchi = Holbigotchi(
                    cohort_id=cohort.id,
                    asset_folder=cohort_data['holbigotchi_asset']
                )
                db.session.add(holbigotchi)
                db.session.commit()
                
                asset_info = holbigotchi.asset_folder
                print(f"✓ Cohorte {cohort_data['name']} créée (ID: {cohort.id}) avec Holbigotchi {asset_info}")
                created_cohorts.append(cohort)
                
            except Exception as e:
                print(f"✗ Erreur lors de la création de la cohorte {cohort_data['name']}: {e}")
                db.session.rollback()
    
    return created_cohorts

def populate_test_users():
    """Crée quelques utilisateurs de test"""
    
    # Récupérer les cohortes existantes
    cohorts = Cohort.query.all()
    
    if not cohorts:
        print("⚠️  Aucune cohorte trouvée. Créez d'abord les cohortes.")
        return
    
    test_users = [
        {
            'email': 'alice@holbertonstudents.com',
            'username': 'alice_c20',
            'password': 'password123',
            'cohort': 'C20'
        },
        {
            'email': 'bob@holbertonstudents.com',
            'username': 'bob_c21',
            'password': 'password123',
            'cohort': 'C21'
        },
        {
            'email': 'charlie@holbertonstudents.com',
            'username': 'charlie_c22',
            'password': 'password123',
            'cohort': 'C22'
        },
        {
            'email': 'diana@holbertonstudents.com',
            'username': 'diana_c23',
            'password': 'password123',
            'cohort': 'C23'
        },
        {
            'email': 'eve@holbertonstudents.com',
            'username': 'eve_c24',
            'password': 'password123',
            'cohort': 'C24'
        }
    ]
    
    for user_data in test_users:
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=user_data['email']).first()
        
        if existing_user:
            print(f"✓ Utilisateur {user_data['email']} existe déjà")
        else:
            # Trouver la cohorte correspondante
            cohort = Cohort.query.filter_by(name=user_data['cohort']).first()
            
            try:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password=user_data['password'],
                    cohort=user_data['cohort'],
                    cohort_id=cohort.id if cohort else None
                )
                
                db.session.add(user)
                db.session.commit()
                
                print(f"✓ Utilisateur {user_data['email']} (@{user_data['username']}) créé avec succès")
                
            except Exception as e:
                print(f"✗ Erreur lors de la création de l'utilisateur {user_data['email']}: {e}")
                db.session.rollback()

def show_database_stats():
    """Affiche les statistiques de la base de données"""
    try:
        cohort_count = Cohort.query.count()
        user_count = User.query.count()
        holbigotchi_count = Holbigotchi.query.count()
        
        print("\n" + "="*60)
        print("📊 STATISTIQUES DE LA BASE DE DONNÉES")
        print("="*60)
        print(f"Cohortes: {cohort_count}")
        print(f"Utilisateurs: {user_count}")
        print(f"Holbigotchi: {holbigotchi_count}")
        print("="*60)
        
        # Afficher les détails des cohortes
        if cohort_count > 0:
            print("\n📚 COHORTES DISPONIBLES:")
            cohorts = Cohort.query.all()
            for cohort in cohorts:
                if cohort.holbigotchi:
                    holbi_hp = cohort.holbigotchi.health_points
                    holbi_state = cohort.holbigotchi.evolution_state
                    holbi_asset = cohort.holbigotchi.asset_folder
                    user_count_in_cohort = User.query.filter_by(cohort_id=cohort.id).count()
                    
                    print(f"  • {cohort.name} - {cohort.description}")
                    print(f"    Holbigotchi: {holbi_hp} HP, État: {holbi_state}, Asset: {holbi_asset}")
                    print(f"    Utilisateurs: {user_count_in_cohort}")
                else:
                    print(f"  • {cohort.name} - {cohort.description}")
                    print(f"    ⚠️  Aucun Holbigotchi associé")
        
        # Afficher les utilisateurs
        if user_count > 0:
            print("\n👥 UTILISATEURS DE TEST:")
            users = User.query.all()
            for user in users:
                print(f"  • {user.email} (@{user.username}) - Cohorte: {user.cohort}")
        
        # Afficher les assets utilisés
        print("\n🎨 ASSETS HOLBIGOTCHI:")
        holbigotchis = Holbigotchi.query.all()
        asset_usage = {}
        for holbi in holbigotchis:
            asset = holbi.asset_folder
            if asset in asset_usage:
                asset_usage[asset] += 1
            else:
                asset_usage[asset] = 1
        
        for asset, count in asset_usage.items():
            print(f"  • {asset}: {count} Holbigotchi")
        
        # Afficher les assets disponibles
        print("\n🎯 ASSETS DISPONIBLES:")
        available_assets = Holbigotchi.get_available_assets()
        for asset in available_assets:
            print(f"  • {asset}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")

def reset_database():
    """Supprime toutes les données et recrée les tables"""
    try:
        print("🗑️  Suppression de toutes les données...")
        
        # Supprimer toutes les tables
        db.drop_all()
        
        # Recréer les tables
        db.create_all()
        
        print("✅ Base de données réinitialisée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")

def main():
    """Fonction principale"""
    import sys
    
    print("🚀 INITIALISATION DE LA BASE DE DONNÉES HOLBIGOTCHI")
    print("="*60)
    
    # Vérifier si l'utilisateur veut réinitialiser
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        confirm = input("⚠️  Êtes-vous sûr de vouloir réinitialiser la base de données? (y/N): ")
        if confirm.lower() == 'y':
            # Créer l'application Flask
            app = create_app('development')
            
            with app.app_context():
                reset_database()
                populate_cohorts()
                populate_test_users()
                show_database_stats()
        else:
            print("Annulé.")
        return
    
    # Créer l'application Flask
    app = create_app('development')
    
    with app.app_context():
        try:
            # Créer les tables si elles n'existent pas
            db.create_all()
            print("✓ Tables de base de données créées/vérifiées")
            
            # Peupler les cohortes
            print("\n📚 Création des cohortes...")
            populate_cohorts()
            
            # Peupler les utilisateurs de test
            print("\n👥 Création des utilisateurs de test...")
            populate_test_users()
            
            # Afficher les statistiques
            show_database_stats()
            
            print("\n🎉 Initialisation terminée avec succès!")
            print("\nVous pouvez maintenant:")
            print("1. Démarrer le serveur: python run.py")
            print("2. Tester l'inscription avec une cohorte existante")
            print("3. Utiliser les utilisateurs de test pour vous connecter")
            print("4. Tester l'API pour changer les assets: /api/holbigotchi/<id>/change-asset")
            
            print("\nCohortes disponibles pour l'inscription:")
            cohorts = Cohort.query.all()
            for cohort in cohorts:
                asset_info = cohort.holbigotchi.asset_folder if cohort.holbigotchi else "Aucun"
                print(f"  - {cohort.name}: {cohort.description} (Asset: {asset_info})")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()