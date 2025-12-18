from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()

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
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(app.root_path), 'static', 'uploads')
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'

    from .routes import main_bp, auth_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app
