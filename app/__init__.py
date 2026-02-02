import os
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

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
    
    # Handle Proxy headers (important for OAuth redirect URIs)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Fernet Key for Untis Password Encryption
    # Must be 32 bytes base64 encoded
    untis_key = os.environ.get('UNTIS_FERNET_KEY')
    if not untis_key:
        # Fallback for dev: derive from SECRET_KEY
        import base64, hashlib
        untis_key = base64.urlsafe_b64encode(hashlib.sha256(app.config['SECRET_KEY'].encode()).digest())
    app.config['UNTIS_FERNET_KEY'] = untis_key

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
    
    # Google Drive Configuration
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    app.config['DRIVE_ENCRYPTION_KEY'] = os.environ.get('DRIVE_ENCRYPTION_KEY')
    app.config['GOOGLE_SERVICE_ACCOUNT_INFO'] = os.environ.get('GOOGLE_SERVICE_ACCOUNT_INFO')
    app.config['GOOGLE_SERVICE_ACCOUNT_FILE'] = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE')
    
    
    # Session Configuration - Enhanced Security
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # Changed from Lax to Strict for better CSRF protection
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
    
    # Content Security Policy (CSP)
    # Optimized for security while supporting the application's needs
    csp = {
        'default-src': '\'self\'',
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\''
        ],
        'img-src': [
            '\'self\'',
            'data:',
            'blob:'
        ],
        'font-src': [
            '\'self\'',
            'data:'
        ],
        'connect-src': [
            '\'self\''
        ],
        'frame-ancestors': '\'none\'',  # Prevent clickjacking attacks
        'base-uri': '\'self\'',         # Restrict base tag URLs
        'form-action': '\'self\'',      # Restrict form submissions to same origin
        'object-src': '\'none\'',       # Block plugins like Flash
        'media-src': '\'self\'',        # Restrict audio/video sources
        'worker-src': '\'self\' blob:'  # Allow service workers
    }

    # Enable Force HTTPS in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # HSTS (HTTP Strict Transport Security) configuration
    # In production: enforce HTTPS for 1 year (31536000 seconds)
    # In development: disable to allow local HTTP testing
    talisman.init_app(app, 
                    content_security_policy=csp, 
                    force_https=is_production,
                    strict_transport_security=is_production,
                    strict_transport_security_max_age=31536000 if is_production else 0,
                    strict_transport_security_include_subdomains=is_production) 
    limiter.init_app(app)
    
    # Additional Security Headers
    @app.after_request
    def set_security_headers(response):
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Additional clickjacking protection
        response.headers['X-Frame-Options'] = 'DENY'
        # Referrer Policy - don't leak referrer information
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Permissions Policy - restrict browser features
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        # Prevent caching of sensitive pages
        if request.endpoint and 'api' in request.endpoint and 'mealplan' not in request.endpoint:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

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
    from .drive_routes import drive_bp
    
    # Exempt API from CSRF protection as we rely on session/login_required and it causes issues in Docker
    csrf.exempt(api_bp)
    csrf.exempt(drive_bp)
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(drive_bp)

    @app.before_request
    def require_login():
        # List of endpoints that do not require login
        public_endpoints = [
            'auth.login',
            'auth.login_page', 
            'static',
            'main.sw',
            'main.manifest',
            'main.setup',
            'api.setup_create_admin',
            'drive.oauth_callback',
            'main.privacy_policy',
            'main.imprint'
        ]
        
        # Also allow if it's a request to static folder directly (outside of blueprint)
        if request.endpoint and 'static' in request.endpoint:
            return

        if request.endpoint and request.endpoint not in public_endpoints:
            # Check if user is authenticated
            from flask_login import current_user
            if not current_user.is_authenticated:
                # If API request, return 401
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Authentication required'}), 401
                # Otherwise redirect to login
                return redirect(url_for('auth.login_page', next=request.url))
            
            # Check Privacy Policy acceptance
            # Exempt the acceptance route itself and logouts/privacy settings
            privacy_exempt = [
                'main.privacy_acceptance',
                'api.accept_privacy',
                'auth.logout',
                'main.privacy_policy',
                'main.imprint'
            ]
            if not current_user.has_accepted_privacy and request.endpoint not in privacy_exempt:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Privacy policy acceptance required', 'require_privacy': True}), 403
                return redirect(url_for('main.privacy_acceptance'))

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
        version = "2.0.0" # Default fallback
        
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
        
        # Schema Update: Add chat_enabled if missing
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            if 'school_class' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('school_class')]
                if 'chat_enabled' not in cols:
                    app.logger.info("Migrating: Adding chat_enabled to school_class")
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE school_class ADD COLUMN chat_enabled BOOLEAN DEFAULT 0"))
                        conn.commit()
        except Exception as e:
            app.logger.error(f"Schema migration error: {e}")

        # Schema Update: Add role if missing
        try:
            if 'user' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('user')]
                if 'role' not in cols:
                    app.logger.info("Migrating: Adding role to user")
                    with db.engine.connect() as conn:
                        # Add column
                        conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'student'"))
                        # Migrate existing admins
                        # Note: We use raw SQL because we can't be sure the boolean columns are in the model anymore,
                        # but they should be in the DB if this is a migration.
                        try:
                            # Try to migrate from old columns if they exist
                            if 'is_super_admin' in cols:
                                conn.execute(text("UPDATE user SET role='super_admin' WHERE is_super_admin=1"))
                            if 'is_admin' in cols:
                                conn.execute(text("UPDATE user SET role='admin' WHERE is_admin=1 AND (is_super_admin=0 OR is_super_admin IS NULL)"))
                        except Exception as ex:
                            app.logger.warning(f"Could not migrate roles from old columns: {ex}")
                        
                        conn.commit()
        except Exception as e:
            app.logger.error(f"Schema migration (role) error: {e}")

        # Schema Update: Comprehensive User Table Update (fix for missing columns)
        try:
            if 'user' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('user')]
                with db.engine.connect() as conn:
                    if 'class_id' not in cols:
                        app.logger.info("Migrating: Adding class_id to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN class_id INTEGER REFERENCES school_class(id)"))
                    if 'dark_mode' not in cols:
                        app.logger.info("Migrating: Adding dark_mode to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN dark_mode BOOLEAN DEFAULT 0"))
                    if 'language' not in cols:
                        app.logger.info("Migrating: Adding language to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN language VARCHAR(5) DEFAULT 'de'"))
                    if 'needs_password_change' not in cols:
                        app.logger.info("Migrating: Adding needs_password_change to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN needs_password_change BOOLEAN DEFAULT 1"))
                    if 'has_seen_tutorial' not in cols:
                        app.logger.info("Migrating: Adding has_seen_tutorial to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN has_seen_tutorial BOOLEAN DEFAULT 0"))
                    if 'has_accepted_privacy' not in cols:
                        app.logger.info("Migrating: Adding has_accepted_privacy to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN has_accepted_privacy BOOLEAN DEFAULT 0"))
                    if 'theme' not in cols:
                        app.logger.info("Migrating: Adding theme to user")
                        conn.execute(text("ALTER TABLE user ADD COLUMN theme VARCHAR(32) DEFAULT 'standard'"))
                    conn.commit()
        except Exception as e:
            app.logger.error(f"User schema migration error: {e}")

        # Schema Update: Add parent_id to task_message if missing
        try:
            if 'task_message' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('task_message')]
                if 'parent_id' not in cols:
                    app.logger.info("Migrating: Adding parent_id to task_message")
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE task_message ADD COLUMN parent_id INTEGER REFERENCES task_message(id)"))
                        conn.commit()
        except Exception as e:
            app.logger.error(f"Schema migration (parent_id) error: {e}")

        # Schema Update: Add notify_chat_message to notification_setting if missing
        try:
            if 'notification_setting' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('notification_setting')]
                if 'notify_chat_message' not in cols:
                    app.logger.info("Migrating: Adding notify_chat_message to notification_setting")
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE notification_setting ADD COLUMN notify_chat_message BOOLEAN DEFAULT 1"))
                        conn.commit()
        except Exception as e:
            app.logger.error(f"Schema migration (notify_chat_message) error: {e}")

        # Schema Update: Fix DriveFolder table (add missing columns)
        try:
            if 'drive_folder' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('drive_folder')]
                with db.engine.connect() as conn:
                    if 'class_id' not in cols:
                        app.logger.info("Migrating: Adding class_id to drive_folder")
                        conn.execute(text("ALTER TABLE drive_folder ADD COLUMN class_id INTEGER REFERENCES school_class(id)"))
                    if 'folder_id' not in cols:
                         # folder_id might be needed if re-creating
                         app.logger.info("Migrating: Adding folder_id to drive_folder")
                         conn.execute(text("ALTER TABLE drive_folder ADD COLUMN folder_id VARCHAR(256)"))
                    if 'file_count' not in cols:
                        app.logger.info("Migrating: Adding file_count to drive_folder")
                        conn.execute(text("ALTER TABLE drive_folder ADD COLUMN file_count INTEGER DEFAULT 0"))
                    if 'is_active' not in cols:
                        app.logger.info("Migrating: Adding is_active to drive_folder")
                        conn.execute(text("ALTER TABLE drive_folder ADD COLUMN is_active BOOLEAN DEFAULT 1"))
                    if 'include_subfolders' not in cols:
                        app.logger.info("Migrating: Adding include_subfolders to drive_folder")
                        conn.execute(text("ALTER TABLE drive_folder ADD COLUMN include_subfolders BOOLEAN DEFAULT 1"))
                    if 'created_by_user_id' not in cols:
                        app.logger.info("Migrating: Adding created_by_user_id to drive_folder")
                        conn.execute(text("ALTER TABLE drive_folder ADD COLUMN created_by_user_id INTEGER REFERENCES user(id)"))
                    conn.commit()
        except Exception as e:
            app.logger.error(f"DriveFolder schema migration error: {e}")


    # Initialize Scheduler
    scheduler.init_app(app)
    
    # Register Jobs
    # Start scheduler for notifications & Drive Warmup
    from app.notifications import check_reminders
    from app.drive_oauth_client import DriveOAuthClient
    from app.untis_service import update_untis_cache_job
    
    def run_drive_warmup():
        with app.app_context():
            client = DriveOAuthClient()
            if client.is_authenticated():
                # Cache structure and file contents (up to 20MB per file)
                client.warmup_cache(depth=3, warmup_content=True)

    # In Gunicorn/Docker, we want it to run. In dev with reloader, only in the main process.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or os.environ.get('GUNICORN_VERSION'):
        try:
            if not scheduler.get_job('check_reminders'):
                scheduler.add_job(id='check_reminders', func=check_reminders, trigger='interval', seconds=45)
            
            # Run Drive Warmup once at startup (after a short delay to let worker boot)
            scheduler.add_job(id='drive_warmup', func=run_drive_warmup, trigger='date', 
                              run_date=datetime.now() + timedelta(seconds=10))
            
            # Periodic Drive Warmup (every 2 hours)
            if not scheduler.get_job('drive_periodic_warmup'):
                scheduler.add_job(id='drive_periodic_warmup', func=run_drive_warmup, trigger='interval', hours=2)
            
            # Untis Cache Jobs
            if not scheduler.get_job('untis_cache_update'):
                scheduler.add_job(id='untis_cache_update', func=update_untis_cache_job, args=[app], 
                                  trigger='interval', minutes=45)
            
            # Initial Untis fetch on startup
            scheduler.add_job(id='untis_initial_fetch', func=update_untis_cache_job, args=[app], 
                              trigger='date', run_date=datetime.now() + timedelta(seconds=15))
            
            if not scheduler.running:
                scheduler.start()
                import atexit
                atexit.register(lambda: scheduler.shutdown(wait=False))
                app.logger.info("--- Background Scheduler Started (Notifications & Warmup) ---")
        except Exception as e:
            app.logger.error(f"Failed to start scheduler: {e}")

    return app
