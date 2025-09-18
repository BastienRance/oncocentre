from flask import Flask
from flask_login import LoginManager
from models import db, User
from routes import main_bp
from auth import auth_bp
from admin import admin_bp
import os
import sqlite3
import bcrypt

def create_app():
    app = Flask(__name__)
    
    # Security configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'carpem-oncocentre-dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oncocentre.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Try SQLAlchemy first, fallback to direct database access
        try:
            return User.query.get(int(user_id))
        except Exception:
            # SQLAlchemy has cached metadata issues, use direct database access
            try:
                conn = sqlite3.connect('oncocentre.db')
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
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)