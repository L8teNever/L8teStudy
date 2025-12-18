import os
import subprocess
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

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

    db.init_app(app)
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

    from .routes import main_bp, auth_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.context_processor
    def inject_version():
        # Default fallback
        version = "1.1.0"
        
        # 1. Try to read from version.txt (pre-generated for production/Docker)
        version_file = os.path.join(app.root_path, '..', 'version.txt')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    return dict(version=f.read().strip())
            except Exception:
                pass
        
        # 2. Try to get it from git (for development)
        try:
            # Use app.root_path to ensure we are in the right directory for git
            commit_count = subprocess.check_output(['git', 'rev-list', '--count', 'HEAD'], 
                                                   stderr=subprocess.STDOUT,
                                                   cwd=app.root_path).decode('utf-8').strip()
            version = f"1.1.{commit_count}"
        except Exception:
            pass
            
        return dict(version=version)

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # If multiple workers try to create the tables at the same time,
            # one might fail with "table already exists". We can safely ignore this.
            if 'already exists' in str(e):
                pass
            else:
                raise e
        
        # Create default admin user if no users exist
        from .models import User
        if User.query.first() is None:
            default_admin = User(username='admin', is_admin=True)
            default_admin.set_password('admin')
            db.session.add(default_admin)
            try:
                db.session.commit()
                print("\n" + "="*60)
                print("  DEFAULT ADMIN ACCOUNT CREATED")
                print("  Username: admin")
                print("  Password: admin")
                print("  ⚠️  PLEASE CHANGE THIS PASSWORD IMMEDIATELY!")
                print("="*60 + "\n")
            except Exception:
                db.session.rollback()

    return app
