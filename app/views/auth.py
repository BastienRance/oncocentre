"""
Authentication routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db
from ..forms import LoginForm
import os
import sqlite3
import bcrypt

auth_bp = Blueprint('auth', __name__)

# Whitelist of authorized usernames
def get_authorized_users():
    """Get authorized users from environment variable"""
    users_str = os.environ.get('AUTHORIZED_USERS', 'admin,user1,user2,doctor1,researcher1')
    return set(user.strip() for user in users_str.split(',') if user.strip())

def get_user_direct(username):
    """Get user directly from database (fallback when SQLAlchemy has cached metadata issues)"""
    try:
        conn = sqlite3.connect('instance/oncocentre.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, is_active, is_admin FROM user WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Create a simple user object
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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Refresh authorized users list (in case environment changed)
        current_authorized_users = get_authorized_users()
        
        # Check if user is in whitelist
        if username not in current_authorized_users:
            flash(f'Accès non autorisé pour cet utilisateur "{username}". Utilisateurs autorisés: {", ".join(sorted(current_authorized_users))}', 'error')
            return render_template('login.html', form=form)
        
        # Find user in database (with fallback for SQLAlchemy caching issues)
        user = None
        try:
            user = User.query.filter_by(username=username).first()
        except Exception:
            # SQLAlchemy has cached metadata issues, use direct database access
            user = get_user_direct(username)
        
        if not user:
            flash(f'Utilisateur "{username}" non trouvé dans la base de données.', 'error')
            return render_template('login.html', form=form)
        
        if not user.is_active:
            flash(f'Compte utilisateur "{username}" désactivé.', 'error')
            return render_template('login.html', form=form)
        
        if not user.check_password(password):
            flash('Mot de passe incorrect.', 'error')
            return render_template('login.html', form=form)
        
        # All checks passed - login successful
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        flash(f'Connexion réussie. Bienvenue {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f'Déconnexion réussie. Au revoir {username}!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/create_initial_user')
def create_initial_user():
    """Create initial admin user for testing - remove in production"""
    if User.query.count() == 0:
        admin_user = User(username='admin')
        admin_user.set_password('admin123')  # Change this in production
        db.session.add(admin_user)
        db.session.commit()
        flash('Utilisateur admin initial créé avec succès.', 'success')
    else:
        flash('Des utilisateurs existent déjà.', 'warning')
    return redirect(url_for('auth.login'))