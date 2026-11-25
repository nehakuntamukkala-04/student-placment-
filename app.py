"""
app.py – Flask Application Factory
Student Placement Readiness Dashboard
"""
import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import db, User

# ---------------------------------------------------------------------------
# Extensions (initialised without app first)
# ---------------------------------------------------------------------------
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Jinja helpers
    app.jinja_env.globals.update(enumerate=enumerate)
    app.jinja_env.filters['enumerate'] = enumerate

    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = 'strong'

    # -----------------------------------------------------------------------
    # Register blueprints
    # -----------------------------------------------------------------------
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)                      # /login  /register  /logout
    app.register_blueprint(student_bp, url_prefix='/student')  # /student/*
    app.register_blueprint(admin_bp,   url_prefix='/admin')    # /admin/*
    app.register_blueprint(api_bp,     url_prefix='/api')      # /api/*

    # -----------------------------------------------------------------------
    # Root redirect
    # -----------------------------------------------------------------------
    @app.route('/')
    def index():
        return render_template('landing.html')

    # -----------------------------------------------------------------------
    # Error handlers
    # -----------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/404.html'), 403

    # -----------------------------------------------------------------------
    # Create all database tables (safe – does nothing if tables exist)
    # -----------------------------------------------------------------------
    with app.app_context():
        db.create_all()

    return app


# ---------------------------------------------------------------------------
# Flask-Login user loader
# ---------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    app.run(debug=debug, host='0.0.0.0', port=port)
