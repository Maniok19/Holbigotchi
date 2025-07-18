from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.cohort import Cohort
from app import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not data or not all(key in data for key in ['email', 'username', 'password', 'cohort']):
            return jsonify({
                'success': False,
                'message': 'Email, nom d\'utilisateur, mot de passe et cohorte sont requis'
            }), 400
        
        email = data['email'].strip().lower()
        username = data['username'].strip()
        password = data['password']
        cohort_name = data['cohort'].strip()
        
        # Validation de l'email
        if not User.validate_email(email):
            return jsonify({
                'success': False,
                'message': 'L\'email doit se terminer par @holbertonstudents.com'
            }), 400
        
        # Validation du nom d'utilisateur
        if not User.validate_username(username):
            return jsonify({
                'success': False,
                'message': 'Le nom d\'utilisateur doit contenir entre 3 et 50 caractères et ne peut contenir que des lettres, chiffres et underscores'
            }), 400
        
        # Vérification que l'email n'existe pas déjà
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Cet email est déjà utilisé'
            }), 409
        
        # Vérification que le nom d'utilisateur n'existe pas déjà
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Ce nom d\'utilisateur est déjà utilisé'
            }), 409
        
        # Validation du mot de passe
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Le mot de passe doit contenir au moins 6 caractères'
            }), 400
        
        # Trouver la cohorte correspondante
        cohort = Cohort.query.filter_by(name=cohort_name).first()
        if not cohort:
            return jsonify({
                'success': False,
                'message': f'La cohorte {cohort_name} n\'existe pas'
            }), 400
        
        # Création de l'utilisateur avec l'ID de la cohorte
        user = User(email=email, username=username, password=password, cohort=cohort_name, cohort_id=cohort.id)
        user.save()
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not data or not all(key in data for key in ['email', 'password']):
            return jsonify({
                'success': False,
                'message': 'Email et mot de passe sont requis'
            }), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Recherche de l'utilisateur
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Email ou mot de passe incorrect'
            }), 401
        
        # Création du token JWT
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500