
"""
Career Roadmap Generator - Main Flask Application.
Production-ready AI-powered career guidance platform.
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
import os

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Register Blueprints
from routes.auth import auth_bp
from routes.resume import resume_bp
from routes.roadmap import roadmap_bp
from routes.skills import skills_bp
from routes.certifications import certifications_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(resume_bp, url_prefix='/api/resume')
app.register_blueprint(roadmap_bp, url_prefix='/api/roadmap')
app.register_blueprint(skills_bp, url_prefix='/api/skills')
app.register_blueprint(certifications_bp, url_prefix='/api/certifications')


# Serve frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# Health check
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Career Roadmap Generator API',
        'version': '1.0.0'
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print(f"""
==========================================================
        AI Career Roadmap Generator API Server            
----------------------------------------------------------
  Server running on http://localhost:{Config.PORT}                
  Frontend: http://localhost:{Config.PORT}                       
  API Base: http://localhost:{Config.PORT}/api                   
  Health:   http://localhost:{Config.PORT}/api/health             
==========================================================
    """)
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )
