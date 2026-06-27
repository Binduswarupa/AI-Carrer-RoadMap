"""
Skills Routes.
Handles skill gap analysis and AI career chat.
"""
from flask import Blueprint, request, jsonify
import datetime
from routes.auth import token_required

skills_bp = Blueprint('skills', __name__)


def get_collections():
    """Lazy import to avoid circular imports."""
    from database import chat_history_collection, progress_collection
    return chat_history_collection, progress_collection


@skills_bp.route('/gap-analysis', methods=['POST'])
@token_required
def skill_gap_analysis(current_user):
    """Perform skill gap analysis using AI."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    current_skills = data.get('current_skills', '').strip()
    education = data.get('education', '').strip()
    experience = data.get('experience', '').strip()
    target_role = data.get('target_role', '').strip()

    if not target_role:
        return jsonify({'error': 'Target role is required'}), 400

    try:
        from services.groq_service import groq_service
        gap_analysis = groq_service.analyze_skill_gap(
            current_skills, education, experience, target_role
        )

        return jsonify({
            'message': 'Skill gap analysis completed',
            'analysis': gap_analysis
        }), 200

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@skills_bp.route('/chat', methods=['POST'])
@token_required
def career_chat(current_user):
    """AI Career Mentor chat endpoint."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    message = data.get('message', '').strip()
    context = data.get('context', '')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        from services.groq_service import groq_service
        response = groq_service.career_chat(message, context)

        # Store chat history
        chat_history, _ = get_collections()
        chat_history.insert_one({
            'user_id': current_user['_id'],
            'message': message,
            'response': response,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })

        return jsonify({
            'response': response
        }), 200

    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500


@skills_bp.route('/chat/history', methods=['GET'])
@token_required
def get_chat_history(current_user):
    """Get chat history for current user."""
    chat_history, _ = get_collections()
    history = list(
        chat_history.find({'user_id': current_user['_id']})
        .sort('timestamp', -1)
        .limit(50)
    )

    for item in history:
        item['_id'] = str(item['_id'])

    return jsonify({'history': history}), 200


@skills_bp.route('/progress', methods=['GET'])
@token_required
def get_progress(current_user):
    """Get user's learning progress."""
    _, progress_col = get_collections()
    progress = progress_col.find_one({'user_id': current_user['_id']})

    if not progress:
        progress = {
            'user_id': current_user['_id'],
            'skills_completed': [],
            'certifications_completed': [],
            'projects_completed': [],
            'learning_streak': 0,
            'total_hours': 0,
            'badges': [],
            'last_activity': None
        }
        progress_col.insert_one(progress)

    progress['_id'] = str(progress.get('_id', ''))
    return jsonify({'progress': progress}), 200


@skills_bp.route('/progress', methods=['PUT'])
@token_required
def update_progress(current_user):
    """Update user's learning progress."""
    data = request.get_json()
    _, progress_col = get_collections()

    update_data = {}
    if 'skill_completed' in data:
        update_data['$addToSet'] = {'skills_completed': data['skill_completed']}
    if 'certification_completed' in data:
        update_data.setdefault('$addToSet', {})['certifications_completed'] = data['certification_completed']
    if 'project_completed' in data:
        update_data.setdefault('$addToSet', {})['projects_completed'] = data['project_completed']
    if 'hours' in data:
        update_data['$inc'] = {'total_hours': data['hours']}

    update_data.setdefault('$set', {})['last_activity'] = datetime.datetime.utcnow().isoformat()

    progress_col.update_one(
        {'user_id': current_user['_id']},
        update_data,
        upsert=True
    )

    # Check for badges
    progress = progress_col.find_one({'user_id': current_user['_id']})
    _check_badges(progress_col, current_user['_id'], progress)

    return jsonify({'message': 'Progress updated successfully'}), 200


def _check_badges(progress_col, user_id, progress):
    """Check and award achievement badges."""
    badges = []
    skills_count = len(progress.get('skills_completed', []))
    certs_count = len(progress.get('certifications_completed', []))
    projects_count = len(progress.get('projects_completed', []))

    if skills_count >= 5:
        badges.append({'name': 'Skill Starter', 'icon': '🌟', 'earned_at': datetime.datetime.utcnow().isoformat()})
    if skills_count >= 15:
        badges.append({'name': 'Skill Master', 'icon': '💎', 'earned_at': datetime.datetime.utcnow().isoformat()})
    if certs_count >= 1:
        badges.append({'name': 'Certified Pro', 'icon': '🏅', 'earned_at': datetime.datetime.utcnow().isoformat()})
    if projects_count >= 3:
        badges.append({'name': 'Project Builder', 'icon': '🚀', 'earned_at': datetime.datetime.utcnow().isoformat()})
    if projects_count >= 5:
        badges.append({'name': 'Portfolio Star', 'icon': '⭐', 'earned_at': datetime.datetime.utcnow().isoformat()})

    if badges:
        progress_col.update_one(
            {'user_id': user_id},
            {'$set': {'badges': badges}}
        )
