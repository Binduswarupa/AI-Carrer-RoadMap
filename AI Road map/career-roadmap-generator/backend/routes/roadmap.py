"""
Roadmap Routes.
Handles career roadmap generation and retrieval.
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
import datetime
from routes.auth import token_required

roadmap_bp = Blueprint('roadmap', __name__)


def get_collections():
    """Lazy import to avoid circular imports."""
    from database import roadmaps_collection
    return roadmaps_collection


@roadmap_bp.route('/generate', methods=['POST'])
@token_required
def generate_roadmap(current_user):
    """Generate a personalized career roadmap using AI."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    target_role = data.get('target_role', '').strip()
    current_skills = data.get('current_skills', '').strip()
    experience_level = data.get('experience_level', 'beginner').strip()
    timeline = data.get('timeline', '6 months').strip()

    if not target_role:
        return jsonify({'error': 'Target role is required'}), 400

    try:
        from services.groq_service import groq_service
        roadmap_data = groq_service.generate_roadmap(
            target_role, current_skills, experience_level, timeline
        )

        roadmaps = get_collections()

        roadmap_doc = {
            'user_id': current_user['_id'],
            'target_role': target_role,
            'current_skills': current_skills,
            'experience_level': experience_level,
            'timeline': timeline,
            'roadmap': roadmap_data,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'progress': {
                'completed_months': 0,
                'completed_tasks': [],
                'overall_progress': 0
            }
        }

        # Update or insert
        existing = roadmaps.find_one({
            'user_id': current_user['_id'],
            'target_role': target_role
        })

        if existing:
            roadmaps.update_one(
                {'_id': existing['_id']},
                {'$set': roadmap_doc}
            )
        else:
            roadmaps.insert_one(roadmap_doc)

        return jsonify({
            'message': 'Roadmap generated successfully',
            'roadmap': roadmap_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'Roadmap generation failed: {str(e)}'}), 500


@roadmap_bp.route('/list', methods=['GET'])
@token_required
def list_roadmaps(current_user):
    """List all roadmaps for the current user."""
    roadmaps = get_collections()
    user_roadmaps = list(roadmaps.find({'user_id': current_user['_id']}).sort('created_at', -1))

    for rm in user_roadmaps:
        rm['_id'] = str(rm['_id'])

    return jsonify({'roadmaps': user_roadmaps}), 200


@roadmap_bp.route('/<roadmap_id>', methods=['GET'])
@token_required
def get_roadmap(current_user, roadmap_id):
    """Get a specific roadmap."""
    roadmaps = get_collections()

    try:
        roadmap = roadmaps.find_one({
            '_id': ObjectId(roadmap_id),
            'user_id': current_user['_id']
        })
    except Exception:
        return jsonify({'error': 'Invalid roadmap ID'}), 400

    if not roadmap:
        return jsonify({'error': 'Roadmap not found'}), 404

    roadmap['_id'] = str(roadmap['_id'])
    return jsonify({'roadmap': roadmap}), 200


@roadmap_bp.route('/career-prediction', methods=['POST'])
@token_required
def career_prediction(current_user):
    """Get career prediction scores."""
    data = request.get_json()

    skills = data.get('skills', '')
    education = data.get('education', '')
    experience = data.get('experience', '')
    target_role = data.get('target_role', '')

    if not target_role:
        return jsonify({'error': 'Target role is required'}), 400

    try:
        from services.groq_service import groq_service
        prediction = groq_service.career_prediction(skills, education, experience, target_role)

        return jsonify({
            'message': 'Career prediction generated',
            'prediction': prediction
        }), 200

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@roadmap_bp.route('/learning-resources', methods=['POST'])
@token_required
def get_learning_resources(current_user):
    """Get learning resources for a topic."""
    data = request.get_json()
    topic = data.get('topic', '')
    level = data.get('level', 'beginner')

    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    try:
        from services.groq_service import groq_service
        resources = groq_service.learning_resources(topic, level)
        return jsonify({'resources': resources}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get resources: {str(e)}'}), 500


@roadmap_bp.route('/interview-questions', methods=['POST'])
@token_required
def get_interview_questions(current_user):
    """Generate interview questions for a role."""
    data = request.get_json()
    role = data.get('role', '')
    difficulty = data.get('difficulty', 'mixed')

    if not role:
        return jsonify({'error': 'Role is required'}), 400

    try:
        from services.groq_service import groq_service
        questions = groq_service.generate_interview_questions(role, difficulty)
        return jsonify({'questions': questions}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate questions: {str(e)}'}), 500
