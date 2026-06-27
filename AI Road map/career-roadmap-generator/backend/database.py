"""
Database module for MongoDB Atlas connection.
Provides database instance and collection references.
"""
from pymongo import MongoClient
from config import Config
import certifi


def get_database():
    """Create and return MongoDB database connection."""
    client = MongoClient(
        Config.MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    try:
        db = client.get_default_database()
    except Exception:
        db = client['career_roadmap']

    # Create indexes for better performance
    _create_indexes(db)

    return db


def _create_indexes(db):
    """Create necessary indexes for collections."""
    try:
        db.users.create_index('email', unique=True)
        db.resumes.create_index('user_id')
        db.roadmaps.create_index('user_id')
        db.certifications.create_index('user_id')
        db.progress.create_index('user_id')
        db.chat_history.create_index('user_id')
    except Exception as e:
        print(f"Index creation warning: {e}")


# Collection references
db = get_database()
users_collection = db['users']
resumes_collection = db['resumes']
roadmaps_collection = db['roadmaps']
certifications_collection = db['certifications']
progress_collection = db['progress']
projects_collection = db['projects']
chat_history_collection = db['chat_history']
