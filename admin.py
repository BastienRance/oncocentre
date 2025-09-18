from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from models import User, Patient, db
from forms import CreateUserForm, EditUserForm
import os
import sqlite3
import bcrypt

admin_bp = Blueprint('admin', __name__)

def get_stats_direct():
    """Get statistics directly from database (fallback for SQLAlchemy caching)"""
    try:
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        
        # Get user counts
        cursor.execute("SELECT COUNT(*) FROM user")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE is_active = 1")
        active_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE is_admin = 1")
        admin_users = cursor.fetchone()[0]
        
        # Get patient count
        cursor.execute("SELECT COUNT(*) FROM patient")
        total_patients = cursor.fetchone()[0]
        
        # Get recent users
        cursor.execute("SELECT id, username, created_at FROM user ORDER BY created_at DESC LIMIT 5")
        recent_users_data = cursor.fetchall()
        
        conn.close()
        
        # Create simple user objects for recent users
        recent_users = []
        for user_id, username, created_at in recent_users_data:
            # Create a simple object with attributes like SQLAlchemy models
            class SimpleUser:
                def __init__(self, user_id, username, created_at):
                    self.id = user_id
                    self.username = username
                    self.created_at = created_at
            
            # Parse datetime string if needed
            from datetime import datetime
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except:
                    created_at = datetime.now()
            
            recent_users.append(SimpleUser(user_id, username, created_at))
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'total_patients': total_patients,
            'recent_users': recent_users
        }
    except Exception:
        # If direct access fails, return zeros
        return {
            'total_users': 0,
            'active_users': 0,
            'admin_users': 0,
            'total_patients': 0,
            'recent_users': []
        }

def get_all_users_direct():
    """Get all users directly from database (fallback for SQLAlchemy caching)"""
    try:
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, username, password_hash, is_active, is_admin, created_at FROM user ORDER BY created_at DESC")
        users_data = cursor.fetchall()
        
        conn.close()
        
        # Create simple user objects
        users = []
        for user_id, username, password_hash, is_active, is_admin, created_at in users_data:
            class SimpleUser:
                def __init__(self, user_id, username, password_hash, is_active, is_admin, created_at):
                    self.id = user_id
                    self.username = username
                    self.password_hash = password_hash
                    self.is_active = bool(is_active)
                    self.is_admin = bool(is_admin)
                    self.created_at = created_at
                    self.patient_count = 0  # Default value
            
            # Parse datetime string if needed
            from datetime import datetime
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except:
                    created_at = datetime.now()
            
            users.append(SimpleUser(user_id, username, password_hash, is_active, is_admin, created_at))
        
        return users
    except Exception:
        return []

def create_user_direct(username, password, is_admin=False):
    """Create user directly in database (fallback for SQLAlchemy caching)"""
    try:
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        
        # Hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Insert user
        cursor.execute('''
            INSERT INTO user (username, password_hash, is_active, is_admin)
            VALUES (?, ?, 1, ?)
        ''', (username, password_hash, is_admin))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_user_by_id_direct(user_id):
    """Get user by ID directly from database (fallback for SQLAlchemy caching)"""
    try:
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, password_hash, is_active, is_admin, created_at FROM user WHERE id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username, password_hash, is_active, is_admin, created_at = result
            
            # Create a simple user object
            class SimpleUser:
                def __init__(self, user_id, username, password_hash, is_active, is_admin, created_at):
                    self.id = user_id
                    self.username = username
                    self.password_hash = password_hash
                    self.is_active = bool(is_active)
                    self.is_admin = bool(is_admin)
                    self.created_at = created_at
                
                def set_password(self, password):
                    # Not implemented for direct access
                    pass
            
            # Parse datetime if needed
            from datetime import datetime
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except:
                    created_at = datetime.now()
            
            return SimpleUser(user_id, username, password_hash, is_active, is_admin, created_at)
        return None
    except Exception:
        return None

def update_user_direct(user_id, is_active, is_admin, new_password=None):
    """Update user directly in database (fallback for SQLAlchemy caching)"""
    try:
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        
        if new_password:
            # Hash new password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            cursor.execute('''
                UPDATE user SET is_active = ?, is_admin = ?, password_hash = ?
                WHERE id = ?
            ''', (is_active, is_admin, password_hash, user_id))
        else:
            cursor.execute('''
                UPDATE user SET is_active = ?, is_admin = ?
                WHERE id = ?
            ''', (is_active, is_admin, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Accès refusé. Privilèges administrateur requis.', 'error')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def update_authorized_users_env():
    """Update AUTHORIZED_USERS environment variable with active users"""
    active_users = User.query.filter_by(is_active=True).all()
    user_list = [user.username for user in active_users]
    os.environ['AUTHORIZED_USERS'] = ','.join(user_list)
    
    # Update auth module
    import auth
    auth.AUTHORIZED_USERS = auth.get_authorized_users()

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Try SQLAlchemy first, fallback to direct database access
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        total_patients = Patient.query.count()
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'total_patients': total_patients,
            'recent_users': recent_users
        }
    except Exception:
        # SQLAlchemy has cached metadata issues, use direct database access
        stats = get_stats_direct()
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@admin_required
def list_users():
    """List all users for administration"""
    # Try SQLAlchemy first, fallback to direct database access
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        # Add patient count for each user
        for user in users:
            user.patient_count = Patient.query.filter_by(created_by=user.id).count()
    except Exception:
        # SQLAlchemy has cached metadata issues, use direct database access
        users = get_all_users_direct()
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user"""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        # Try SQLAlchemy first, fallback to direct database access
        username = form.username.data
        password = form.password.data
        is_admin = form.is_admin.data
        
        success = False
        try:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            success = True
        except Exception:
            # SQLAlchemy has cached metadata issues, use direct database access
            try:
                db.session.rollback()
            except:
                pass
            success = create_user_direct(username, password, is_admin)
        
        if success:
            # Update authorized users environment variable
            try:
                update_authorized_users_env()
            except:
                pass  # Don't fail if environment update fails
            
            flash(f'Utilisateur "{username}" créé avec succès.', 'success')
            return redirect(url_for('admin.list_users'))
        else:
            flash('Erreur lors de la création de l\'utilisateur.', 'error')
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit an existing user"""
    # Try SQLAlchemy first, fallback to direct database access
    user = None
    try:
        user = User.query.get_or_404(user_id)
    except Exception:
        # SQLAlchemy has cached metadata issues, use direct database access
        user = get_user_by_id_direct(user_id)
        if not user:
            flash('Utilisateur non trouvé.', 'error')
            return redirect(url_for('admin.list_users'))
    
    # Prevent admin from disabling themselves
    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre compte.', 'warning')
        return redirect(url_for('admin.list_users'))
    
    form = EditUserForm()
    
    if form.validate_on_submit():
        is_active = form.is_active.data
        is_admin = form.is_admin.data
        new_password = form.reset_password.data if form.reset_password.data else None
        
        # Try SQLAlchemy first, fallback to direct database access
        success = False
        try:
            user.is_active = is_active
            user.is_admin = is_admin
            
            if new_password:
                user.set_password(new_password)
            
            db.session.commit()
            success = True
        except Exception:
            # SQLAlchemy has cached metadata issues, use direct database access
            try:
                db.session.rollback()
            except:
                pass
            success = update_user_direct(user_id, is_active, is_admin, new_password)
        
        if success:
            # Update authorized users environment variable
            try:
                update_authorized_users_env()
            except:
                pass  # Don't fail if environment update fails
            
            flash(f'Utilisateur "{user.username}" modifié avec succès.', 'success')
            return redirect(url_for('admin.list_users'))
        else:
            flash('Erreur lors de la modification de l\'utilisateur.', 'error')
    
    # Pre-populate form
    if request.method == 'GET':
        form.is_active.data = user.is_active
        form.is_admin.data = user.is_admin
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete/deactivate a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'error')
        return redirect(url_for('admin.list_users'))
    
    # Check if user has patients
    patient_count = Patient.query.filter_by(created_by=user.id).count()
    
    if patient_count > 0:
        # Deactivate instead of delete if user has patients
        user.is_active = False
        action = "désactivé"
    else:
        # Safe to delete if no patients
        db.session.delete(user)
        action = "supprimé"
    
    try:
        db.session.commit()
        
        # Update authorized users environment variable
        update_authorized_users_env()
        
        flash(f'Utilisateur "{user.username}" {action} avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/<int:user_id>/patients')
@admin_required
def user_patients(user_id):
    """View patients created by a specific user"""
    user = User.query.get_or_404(user_id)
    patients = Patient.query.filter_by(created_by=user.id).order_by(Patient.created_at.desc()).all()
    
    return render_template('admin/user_patients.html', user=user, patients=patients)

@admin_bp.route('/system/info')
@admin_required
def system_info():
    """System information and configuration"""
    import auth
    
    info = {
        'authorized_users': sorted(auth.get_authorized_users()),
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'admin_users': User.query.filter_by(is_admin=True).count(),
        'total_patients': Patient.query.count(),
        'encryption_key_exists': os.path.exists('encryption.key'),
        'database_path': 'oncocentre.db'
    }
    
    return render_template('admin/system_info.html', info=info)