from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.cohort import Cohort
from app.models.holbigotchi import Holbigotchi
from app.models.user import User
from app import db

cohorts_bp = Blueprint('cohorts', __name__)

@cohorts_bp.route('/', methods=['GET'])
def get_all_cohorts():  # Supprimé @jwt_required() pour permettre l'accès public
    """Récupère toutes les cohortes"""
    try:
        cohorts = Cohort.query.all()
        return jsonify({
            'success': True,
            'cohorts': [cohort.to_dict() for cohort in cohorts],
            'count': len(cohorts)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des cohortes'
        }), 500

@cohorts_bp.route('/<int:cohort_id>', methods=['GET'])
@jwt_required()
def get_cohort(cohort_id):
    """Récupère une cohorte spécifique"""
    try:
        cohort = Cohort.query.get(cohort_id)
        if not cohort:
            return jsonify({
                'success': False,
                'message': 'Cohorte non trouvée'
            }), 404
        
        # Inclure les informations sur le Holbigotchi associé
        cohort_data = cohort.to_dict()
        if cohort.holbigotchi:
            cohort_data['holbigotchi'] = cohort.holbigotchi.to_dict()
        
        return jsonify({
            'success': True,
            'cohort': cohort_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération de la cohorte'
        }), 500

@cohorts_bp.route('/', methods=['POST'])
@jwt_required()
def create_cohort():
    """Crée une nouvelle cohorte"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Le nom de la cohorte est requis'
            }), 400
        
        name = data['name'].strip()
        description = data.get('description', '').strip()
        
        # Vérifier que la cohorte n'existe pas déjà
        existing_cohort = Cohort.query.filter_by(name=name).first()
        if existing_cohort:
            return jsonify({
                'success': False,
                'message': 'Une cohorte avec ce nom existe déjà'
            }), 409
        
        # Créer la cohorte
        cohort = Cohort(name=name, description=description)
        cohort.save()
        
        # Créer automatiquement un Holbigotchi pour cette cohorte
        holbigotchi = Holbigotchi(cohort_id=cohort.id)
        holbigotchi.save()
        
        return jsonify({
            'success': True,
            'message': 'Cohorte créée avec succès',
            'cohort': cohort.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la création de la cohorte'
        }), 500

@cohorts_bp.route('/<int:cohort_id>', methods=['PUT'])
@jwt_required()
def update_cohort(cohort_id):
    """Met à jour une cohorte"""
    try:
        cohort = Cohort.query.get(cohort_id)
        if not cohort:
            return jsonify({
                'success': False,
                'message': 'Cohorte non trouvée'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Données manquantes'
            }), 400
        
        # Mettre à jour les champs
        if 'name' in data:
            name = data['name'].strip()
            # Vérifier l'unicité du nom
            existing_cohort = Cohort.query.filter_by(name=name).first()
            if existing_cohort and existing_cohort.id != cohort_id:
                return jsonify({
                    'success': False,
                    'message': 'Une cohorte avec ce nom existe déjà'
                }), 409
            cohort.name = name
        
        if 'description' in data:
            cohort.description = data['description'].strip()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cohorte mise à jour avec succès',
            'cohort': cohort.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la mise à jour de la cohorte'
        }), 500

@cohorts_bp.route('/<int:cohort_id>', methods=['DELETE'])
@jwt_required()
def delete_cohort(cohort_id):
    """Supprime une cohorte et son Holbigotchi associé"""
    try:
        cohort = Cohort.query.get(cohort_id)
        if not cohort:
            return jsonify({
                'success': False,
                'message': 'Cohorte non trouvée'
            }), 404
        
        # Supprimer le Holbigotchi associé (cascade)
        if cohort.holbigotchi:
            cohort.holbigotchi.delete()
        
        # Supprimer la cohorte
        cohort.delete()
        
        return jsonify({
            'success': True,
            'message': 'Cohorte supprimée avec succès'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la suppression de la cohorte'
        }), 500

@cohorts_bp.route('/<int:cohort_id>/users', methods=['GET'])
@jwt_required()
def get_cohort_users(cohort_id):
    """Récupère tous les utilisateurs d'une cohorte"""
    try:
        cohort = Cohort.query.get(cohort_id)
        if not cohort:
            return jsonify({
                'success': False,
                'message': 'Cohorte non trouvée'
            }), 404
        
        users = User.query.filter_by(cohort_id=cohort_id).all()
        
        return jsonify({
            'success': True,
            'cohort': cohort.to_dict(),
            'users': [user.to_dict() for user in users],
            'count': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des utilisateurs'
        }), 500