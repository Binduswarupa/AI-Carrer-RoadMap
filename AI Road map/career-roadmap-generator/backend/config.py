"""
Configuration module for the Career Roadmap Generator.
Loads environment variables and provides configuration constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""

    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET', 'fallback-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1')
    PORT = int(os.getenv('PORT', 5000))

    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/career_roadmap')

    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = 'llama-3.3-70b-versatile'

    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'fallback-secret-key')
    JWT_EXPIRATION_HOURS = 24

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'pdf'}

    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000',
                    'http://localhost:5500', 'http://127.0.0.1:5500',
                    'http://localhost:8000', 'http://127.0.0.1:8000']
