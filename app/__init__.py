"""
Application factory for the CARPEM Oncocentre Flask application
"""

from flask import Flask
from flask_login import LoginManager
import os
import sqlite3
import bcrypt

def create_app(config_name='default'):
    """Create and configure the Flask application"""
    # Flask app needs to find templates and static files in parent directory
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration
    from .config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from .models import db
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Try SQLAlchemy first, fallback to direct database access
        from .models import User
        try:
            return User.query.get(int(user_id))
        except Exception:
            # SQLAlchemy has cached metadata issues, use direct database access
            try:
                conn = sqlite3.connect('instance/oncocentre.db')
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash, is_active, is_admin FROM user WHERE id = ?",
                    (int(user_id),)
                )
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    # Create a simple user object compatible with Flask-Login
                    class DirectUser:
                        def __init__(self, id, username, password_hash, is_active, is_admin):
                            self.id = id
                            self.username = username
                            self.password_hash = password_hash
                            self.is_active = bool(is_active)
                            self.is_admin = bool(is_admin)
                        
                        def check_password(self, password):
                            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
                        
                        def is_authenticated(self):
                            return True
                        
                        def is_anonymous(self):
                            return False
                        
                        def get_id(self):
                            return str(self.id)
                    
                    return DirectUser(*result)
                return None
            except Exception:
                return None
    
    # Register blueprints
    from .views import main_bp, auth_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app