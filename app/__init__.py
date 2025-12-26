import os
import subprocess
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

# Initialize Scheduler global instance
from flask_apscheduler import APScheduler
scheduler = APScheduler()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///l8testudy.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.root_path points to 'app/', but static is in '../static' relative to it. 
    # However, Flask's static_folder arg handles serving. We just need the absolute path to writing files.
    # Since we passed static_folder='../static', app.static_folder should be populated correctly with absolute path?
    # Actually, it's safer to rely on explicit path if we know the structure:
    # L8teStudy/
    #   app/
    #   static/
    #   templates/
    #   instance/ (default for Flask instance_path)
    
    # Secure Uploads: Use 'instance/uploads' or env var 'UPLOAD_FOLDER'
    # In Docker, we map volumes to this location.
    default_upload_path = os.path.join(app.instance_path, 'uploads')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', default_upload_path)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Session Configuration
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days
    # Only set secure cookies in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_SECURE'] = is_production
    app.config['REMEMBER_COOKIE_SECURE'] = is_production
    
    # Fix for CSRF behind reverse proxies (Dockge, Nginx)
    app.config['WTF_CSRF_SSL_STRICT'] = is_production  # Disable strict SSL check unless in prod

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'

    # Security Init
    csrf.init_app(app)
    # CSP is set to None to allow inline scripts/styles for now. 
    # Enable Force HTTPS in production, but careful in dev (Talisman defaults force_https=True).
    # We disable force_https for local dev to avoid redirect loops if no SSL cert is present.
    is_production = os.environ.get('FLASK_ENV') == 'production'
    talisman.init_app(app, content_security_policy=None, force_https=is_production) 
    limiter.init_app(app)

    # Error Handlers for debugging
    from flask_wtf.csrf import CSRFError
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.error(f"CSRF Error: {e.description}")
        return jsonify({'success': False, 'message': 'CSRF Token missing or invalid'}), 400

    @app.errorhandler(400)
    def handle_bad_request(e):
        app.logger.error(f"Bad Request (400): {e}")
        return jsonify({'success': False, 'message': 'Bad Request'}), 400

    from .routes import main_bp, auth_bp, api_bp
    
    # Exempt API from CSRF protection as we rely on session/login_required and it causes issues in Docker
    csrf.exempt(api_bp)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.context_processor
    def utility_processor():
        def t(key):
            # Simple pass-through for server-side rendering
            # The actual translation happens via JS in index.html, 
            # but for login.html we need at least a dummy or simple mapping.
            mapping = {
                'login_title': 'Anmelden',
                'welcome_msg': 'Willkommen bei L8teStudy',
                'login_btn': 'Anmelden',
                'class_code': 'Klassencode',
                'username': 'Benutzername',
                'password': 'Passwort'
            }
            return mapping.get(key, key)
        return dict(t=t)

    def update_version_file():
        version_file = os.path.join(app.root_path, '..', 'version.txt')
        version = "1.1.18" # Default fallback
        
        try:
            commit_count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], 
                                                   stderr=subprocess.STDOUT,
                                                   cwd=app.root_path).decode('utf-8').strip()
            version = f"1.1.{commit_count}"
            try:
                with open(version_file, 'w') as f:
                    f.write(version)
            except Exception:
                pass
        except Exception:
            if os.path.exists(version_file):
                try:
                    with open(version_file, 'r') as f:
                        version = f.read().strip()
                except Exception:
                    pass
        return version

    current_version = update_version_file()

    @app.context_processor
    def inject_version():
        return dict(version=current_version)

    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            app.logger.info("Database tables created/verified successfully")
        except Exception as e:
            # If multiple workers try to create the tables at the same time,
            # or if tables already exist, we can safely continue
            app.logger.warning(f"Database initialization warning: {str(e)}")
            # Try to continue anyway - tables might already exist
            pass
        
        # Create default admin user if no users exist
        # Use a try-except to handle race conditions when multiple workers start simultaneously
        from .models import User
        try:
            if User.query.first() is None:
                default_admin = User(username='admin', is_admin=True)
                default_admin.set_password('admin')
                db.session.add(default_admin)
                db.session.commit()
                app.logger.info("="*60)
                app.logger.info("  DEFAULT ADMIN ACCOUNT CREATED")
                app.logger.info("  Username: admin")
                app.logger.info("  Password: admin")
                app.logger.info("  ⚠️  PLEASE CHANGE THIS PASSWORD IMMEDIATELY!")
                app.logger.info("="*60)
        except Exception as e:
            # If another worker already created the admin, rollback and continue
            db.session.rollback()
            app.logger.debug(f"Admin account creation skipped: {str(e)}")

    # Initialize Scheduler
    scheduler.init_app(app)
    
    # Register Jobs
    # Start scheduler for notifications
    from app.notifications import check_reminders
    # In Gunicorn/Docker, we want it to run. In dev with reloader, only in the main process.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or os.environ.get('GUNICORN_VERSION'):
        try:
            if not scheduler.get_job('check_reminders'):
                scheduler.add_job(id='check_reminders', func=check_reminders, trigger='interval', seconds=45)
            if not scheduler.running:
                scheduler.start()
                app.logger.info("--- Notification Scheduler Started ---")
        except Exception as e:
            app.logger.error(f"Failed to start scheduler: {e}")

    return app
