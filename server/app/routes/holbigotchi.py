from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.holbigotchi import Holbigotchi
from app.models.cohort import Cohort
from app.models.user import User
from app import db
from datetime import datetime

holbigotchi_bp = Blueprint('holbigotchi', __name__)

@holbigotchi_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_holbigotchi():
    """Récupère tous les Holbigotchi"""
    try:
        holbigotchis = Holbigotchi.query.all()
        return jsonify({
            'success': True,
            'holbigotchis': [holbi.to_dict() for holbi in holbigotchis],
            'count': len(holbigotchis)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des Holbigotchi'
        }), 500

@holbigotchi_bp.route('/<int:holbigotchi_id>', methods=['GET'])
@jwt_required()
def get_holbigotchi(holbigotchi_id):
    """Récupère un Holbigotchi spécifique"""
    try:
        holbigotchi = Holbigotchi.query.get(holbigotchi_id)
        if not holbigotchi:
            return jsonify({
                'success': False,
                'message': 'Holbigotchi non trouvé'
            }), 404
        
        return jsonify({
            'success': True,
            'holbigotchi': holbigotchi.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération du Holbigotchi'
        }), 500

@holbigotchi_bp.route('/cohort/<int:cohort_id>', methods=['GET'])
@jwt_required()
def get_cohort_holbigotchi(cohort_id):
    """Récupère le Holbigotchi d'une cohorte spécifique"""
    try:
        holbigotchi = Holbigotchi.query.filter_by(cohort_id=cohort_id).first()
        if not holbigotchi:
            return jsonify({
                'success': False,
                'message': 'Aucun Holbigotchi trouvé pour cette cohorte'
            }), 404
        
        return jsonify({
            'success': True,
            'holbigotchi': holbigotchi.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération du Holbigotchi'
        }), 500

@holbigotchi_bp.route('/<int:holbigotchi_id>/feed', methods=['POST'])
@jwt_required()
def feed_holbigotchi(holbigotchi_id):
    """Nourrit un Holbigotchi"""
    try:
        holbigotchi = Holbigotchi.query.get(holbigotchi_id)
        if not holbigotchi:
            return jsonify({
                'success': False,
                'message': 'Holbigotchi non trouvé'
            }), 404
        
        data = request.get_json()
        health_boost = data.get('health_boost', 10) if data else 10
        
        # Vérifier que le boost est dans une plage acceptable
        health_boost = max(1, min(50, health_boost))
        
        # Nourrir le Holbigotchi
        holbigotchi.feed(health_boost)
        
        return jsonify({
            'success': True,
            'message': f'Holbigotchi nourri avec succès (+{health_boost} HP)',
            'holbigotchi': holbigotchi.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors du nourrissage du Holbigotchi'
        }), 500

@holbigotchi_bp.route('/<int:holbigotchi_id>/evolve', methods=['POST'])
@jwt_required()
def evolve_holbigotchi(holbigotchi_id):
    """Fait évoluer un Holbigotchi"""
    try:
        holbigotchi = Holbigotchi.query.get(holbigotchi_id)
        if not holbigotchi:
            return jsonify({
                'success': False,
                'message': 'Holbigotchi non trouvé'
            }), 404
        
        if not holbigotchi.can_evolve():
            return jsonify({
                'success': False,
                'message': 'Le Holbigotchi ne peut pas évoluer pour le moment',
                'requirements': {
                    'current_state': holbigotchi.evolution_state,
                    'health_points': holbigotchi.health_points,
                    'needed_health': 80 if holbigotchi.evolution_state == 'egg' else 90
                }
            }), 400
        
        # Faire évoluer
        evolved = holbigotchi.evolve()
        
        if evolved:
            return jsonify({
                'success': True,
                'message': f'Holbigotchi a évolué vers {holbigotchi.evolution_state}!',
                'holbigotchi': holbigotchi.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Échec de l\'évolution'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de l\'évolution du Holbigotchi'
        }), 500

@holbigotchi_bp.route('/<int:holbigotchi_id>/health', methods=['PUT'])
@jwt_required()
def update_health(holbigotchi_id):
    """Met à jour la santé d'un Holbigotchi (pour les tâches automatiques)"""
    try:
        holbigotchi = Holbigotchi.query.get(holbigotchi_id)
        if not holbigotchi:
            return jsonify({
                'success': False,
                'message': 'Holbigotchi non trouvé'
            }), 404
        
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({
                'success': False,
                'message': 'Action requise (decay ou boost)'
            }), 400
        
        action = data['action']
        amount = data.get('amount', 5)
        
        if action == 'decay':
            holbigotchi.decay_health(amount)
            message = f'Santé diminuée de {amount} points'
        elif action == 'boost':
            # Assurer que le boost est dans une plage acceptable
            amount = max(1, min(50, amount))
            holbigotchi.health_points = min(100, holbigotchi.health_points + amount)
            db.session.commit()
            message = f'Santé augmentée de {amount} points'
        else:
            return jsonify({
                'success': False,
                'message': 'Action invalide. Utilisez "decay" ou "boost"'
            }), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'holbigotchi': holbigotchi.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la mise à jour de la santé'
        }), 500

@holbigotchi_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Récupère le classement des Holbigotchi"""
    try:
        # Trier par points de santé décroissants, puis par état d'évolution
        holbigotchis = Holbigotchi.query.order_by(
            Holbigotchi.health_points.desc(),
            Holbigotchi.evolution_state.desc()
        ).all()
        
        leaderboard = []
        for i, holbi in enumerate(holbigotchis, 1):
            holbi_data = holbi.to_dict()
            holbi_data['rank'] = i
            holbi_data['cohort_name'] = holbi.cohort.name if holbi.cohort else 'Unknown'
            leaderboard.append(holbi_data)
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'count': len(leaderboard)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération du classement'
        }), 500

@holbigotchi_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_global_stats():
    """Récupère les statistiques globales des Holbigotchi"""
    try:
        total_holbigotchis = Holbigotchi.query.count()
        healthy_count = Holbigotchi.query.filter(Holbigotchi.health_points >= 70).count()
        sick_count = Holbigotchi.query.filter(
            Holbigotchi.health_points >= 30,
            Holbigotchi.health_points < 70
        ).count()
        dead_count = Holbigotchi.query.filter(Holbigotchi.health_points < 30).count()
        
        # Statistiques par état d'évolution
        egg_count = Holbigotchi.query.filter_by(evolution_state='egg').count()
        baby_count = Holbigotchi.query.filter_by(evolution_state='baby').count()
        adult_count = Holbigotchi.query.filter_by(evolution_state='adult').count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_holbigotchis,
                'health_status': {
                    'healthy': healthy_count,
                    'sick': sick_count,
                    'dead': dead_count
                },
                'evolution_stages': {
                    'egg': egg_count,
                    'baby': baby_count,
                    'adult': adult_count
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des statistiques'
        }), 500

@holbigotchi_bp.route('/<int:holbigotchi_id>/change-asset', methods=['PUT'])
@jwt_required()
def change_holbigotchi_asset(holbigotchi_id):
    """Change l'asset d'un Holbigotchi"""
    try:
        holbigotchi = Holbigotchi.query.get(holbigotchi_id)
        if not holbigotchi:
            return jsonify({
                'success': False,
                'message': 'Holbigotchi non trouvé'
            }), 404
        
        data = request.get_json()
        if not data or 'asset_folder' not in data:
            return jsonify({
                'success': False,
                'message': 'Asset folder requis',
                'available_assets': Holbigotchi.get_available_assets()
            }), 400
        
        new_asset = data['asset_folder']
        
        # Vérifier que l'asset existe
        if new_asset not in Holbigotchi.get_available_assets():
            return jsonify({
                'success': False,
                'message': f'Asset "{new_asset}" non disponible',
                'available_assets': Holbigotchi.get_available_assets()
            }), 400
        
        # Changer l'asset
        old_asset = holbigotchi.asset_folder
        holbigotchi.asset_folder = new_asset
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Asset changé de "{old_asset}" vers "{new_asset}"',
            'holbigotchi': holbigotchi.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors du changement d\'asset'
        }), 500

@holbigotchi_bp.route('/assets', methods=['GET'])
@jwt_required()
def get_available_assets():
    """Récupère la liste des assets disponibles"""
    try:
        return jsonify({
            'success': True,
            'assets': Holbigotchi.get_available_assets(),
            'asset_details': Holbigotchi.AVAILABLE_ASSETS
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la récupération des assets'
        }), 500