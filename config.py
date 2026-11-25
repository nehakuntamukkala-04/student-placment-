import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placement-readiness-secret-key-2026-production')
    SQLALCHEMY_DATABASE_URI = db_url or f'sqlite:///{os.path.join(BASE_DIR, "placement.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # don't expire tokens during user session
