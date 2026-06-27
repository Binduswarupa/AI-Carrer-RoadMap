"""
Certifications Routes.
Handles certification recommendations and project suggestions.
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
import datetime
from routes.auth import token_required

certifications_bp = Blueprint('certifications', __name__)


def get_collections():
    """Lazy import to avoid circular imports."""
    from database import certifications_collection, projects_collection
    return certifications_collection, projects_collection


@certifications_bp.route('/recommend', methods=['POST'])
@token_required
def recommend_certifications(current_user):
    """Get AI-powered certification recommendations."""
    data = request.get_json()

    target_role = data.get('target_role', '').strip()
    current_skills = data.get('current_skills', '').strip()
    budget = data.get('budget', 'moderate').strip()

    if not target_role:
        return jsonify({'error': 'Target role is required'}), 400

    try:
        from services.groq_service import groq_service
        recommendations = groq_service.recommend_certifications(
            target_role, current_skills, budget
        )

        # Store recommendations
        certs_col, _ = get_collections()
        certs_col.update_one(
            {'user_id': current_user['_id']},
            {'$set': {
                'user_id': current_user['_id'],
                'target_role': target_role,
                'recommended_certs': recommendations,
                'generated_at': datetime.datetime.utcnow().isoformat()
            }},
            upsert=True
        )

        return jsonify({
            'message': 'Certifications recommended successfully',
            'certifications': recommendations
        }), 200

    except Exception as e:
        return jsonify({'error': f'Recommendation failed: {str(e)}'}), 500


@certifications_bp.route('/list', methods=['GET'])
@token_required
def list_certifications(current_user):
    """Get stored certification recommendations."""
    certs_col, _ = get_collections()
    certs = certs_col.find_one({'user_id': current_user['_id']})

    if not certs:
        return jsonify({'certifications': None}), 200

    certs['_id'] = str(certs['_id'])
    return jsonify({'certifications': certs}), 200


@certifications_bp.route('/projects/recommend', methods=['POST'])
@token_required
def recommend_projects(current_user):
    """Get AI-powered project recommendations."""
    data = request.get_json()

    target_role = data.get('target_role', '').strip()
    current_skills = data.get('current_skills', '').strip()
    experience_level = data.get('experience_level', 'beginner').strip()

    if not target_role:
        return jsonify({'error': 'Target role is required'}), 400

    try:
        from services.groq_service import groq_service
        projects = groq_service.recommend_projects(
            target_role, current_skills, experience_level
        )

        # Store recommendations
        _, projects_col = get_collections()
        projects_col.update_one(
            {'user_id': current_user['_id']},
            {'$set': {
                'user_id': current_user['_id'],
                'target_role': target_role,
                'recommended_projects': projects,
                'generated_at': datetime.datetime.utcnow().isoformat()
            }},
            upsert=True
        )

        return jsonify({
            'message': 'Projects recommended successfully',
            'projects': projects
        }), 200

    except Exception as e:
        return jsonify({'error': f'Project recommendation failed: {str(e)}'}), 500


@certifications_bp.route('/projects/list', methods=['GET'])
@token_required
def list_projects(current_user):
    """Get stored project recommendations."""
    _, projects_col = get_collections()
    projects = projects_col.find_one({'user_id': current_user['_id']})

    if not projects:
        return jsonify({'projects': None}), 200

    projects['_id'] = str(projects['_id'])
    return jsonify({'projects': projects}), 200
