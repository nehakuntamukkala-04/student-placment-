import os
import shutil
import tempfile

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))
TMP_DIR = tempfile.gettempdir()

db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

if not db_url and IS_VERCEL:
    # Vercel's deployment filesystem is read-only; copy pre-seeded DB into temp dir
    src_db = os.path.join(BASE_DIR, 'placement.db')
    tmp_db = os.path.join(TMP_DIR, 'placement.db')
    if os.path.exists(src_db) and not os.path.exists(tmp_db):
        shutil.copy2(src_db, tmp_db)
    sqlite_uri = f'sqlite:///{tmp_db}'
else:
    sqlite_uri = f'sqlite:///{os.path.join(BASE_DIR, "placement.db")}'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'placement-readiness-secret-key-2026-production')
    SQLALCHEMY_DATABASE_URI = db_url or sqlite_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads configuration (use temp dir on Vercel serverless)
    UPLOAD_FOLDER = os.path.join(TMP_DIR, 'uploads') if IS_VERCEL else os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # don't expire tokens during user session
