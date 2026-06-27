"""
Resume Routes.
Handles resume upload, parsing, and AI analysis.
"""
from flask import Blueprint, request, jsonify
from bson import ObjectId
import datetime
from routes.auth import token_required

resume_bp = Blueprint('resume', __name__)


def get_collections():
    """Lazy import to avoid circular imports."""
    from database import resumes_collection
    return resumes_collection


@resume_bp.route('/upload', methods=['POST'])
@token_required
def upload_resume(current_user):
    """Upload and parse a resume PDF."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    try:
        from services.resume_parser import resume_parser
        parsed_data = resume_parser.parse_resume(file)

        resumes = get_collections()

        resume_doc = {
            'user_id': current_user['_id'],
            'filename': file.filename,
            'resume_text': parsed_data['raw_text'],
            'extracted_skills': parsed_data['skills'],
            'education': parsed_data['education'],
            'email': parsed_data['email'],
            'phone': parsed_data['phone'],
            'links': parsed_data['links'],
            'word_count': parsed_data['word_count'],
            'uploaded_at': datetime.datetime.utcnow().isoformat(),
            'analyzed': False
        }

        # Update or insert
        existing = resumes.find_one({'user_id': current_user['_id']})
        if existing:
            resumes.update_one(
                {'user_id': current_user['_id']},
                {'$set': resume_doc}
            )
        else:
            resumes.insert_one(resume_doc)

        return jsonify({
            'message': 'Resume uploaded and parsed successfully',
            'data': {
                'skills': parsed_data['skills'],
                'education': parsed_data['education'],
                'word_count': parsed_data['word_count'],
                'email': parsed_data['email'],
                'links': parsed_data['links']
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/analyze', methods=['POST'])
@token_required
def analyze_resume(current_user):
    """Analyze resume using AI."""
    resumes = get_collections()
    resume = resumes.find_one({'user_id': current_user['_id']})

    if not resume:
        return jsonify({'error': 'No resume found. Please upload a resume first.'}), 404

    try:
        from services.groq_service import groq_service
        analysis = groq_service.analyze_resume(resume['resume_text'])

        # Store analysis results
        resumes.update_one(
            {'user_id': current_user['_id']},
            {'$set': {
                'analysis': analysis,
                'ats_score': analysis.get('ats_score', 0),
                'analyzed': True,
                'analyzed_at': datetime.datetime.utcnow().isoformat()
            }}
        )

        return jsonify({
            'message': 'Resume analyzed successfully',
            'analysis': analysis
        }), 200

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@resume_bp.route('/analysis', methods=['GET'])
@token_required
def get_analysis(current_user):
    """Get stored resume analysis."""
    resumes = get_collections()
    resume = resumes.find_one({'user_id': current_user['_id']})

    if not resume:
        return jsonify({'error': 'No resume found'}), 404

    resume['_id'] = str(resume['_id'])

    return jsonify({
        'resume': {
            'filename': resume.get('filename'),
            'extracted_skills': resume.get('extracted_skills'),
            'education': resume.get('education'),
            'word_count': resume.get('word_count'),
            'analyzed': resume.get('analyzed', False),
            'analysis': resume.get('analysis'),
            'ats_score': resume.get('ats_score', 0),
            'uploaded_at': resume.get('uploaded_at')
        }
    }), 200
