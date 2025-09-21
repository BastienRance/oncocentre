"""
Authentication routes with dual authentication support (Local + LDAP)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from ..core.models import User, db
from .forms import LoginForm
from ..core.ldap_auth import ldap_auth
import os
import sqlite3
import bcrypt
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Whitelist of authorized usernames
def get_authorized_users():
    """Get authorized users from database first, then environment variable as fallback"""
    try:
        from ..core.models import WhitelistEntry
        # Try to get from database first
        db_users = WhitelistEntry.get_authorized_usernames()
        if db_users:
            return db_users
    except Exception as e:
        # Database might not be initialized yet, fall back to environment
        logger.warning(f"Could not access whitelist database: {e}")

    # Fallback to environment variable
    users_str = os.environ.get('AUTHORIZED_USERS', 'admin,user1,user2,doctor1,researcher1')
    return set(user.strip() for user in users_str.split(',') if user.strip())

def get_user_direct(username):
    """Get user directly from database (fallback when SQLAlchemy has cached metadata issues)"""
    try:
        conn = sqlite3.connect('instance/oncocentre.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, is_active, is_admin, auth_source FROM user WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Create a simple user object
            class DirectUser:
                def __init__(self, id, username, password_hash, is_active, is_admin, auth_source):
                    self.id = id
                    self.username = username
                    self.password_hash = password_hash
                    self.is_active = bool(is_active)
                    self.is_admin = bool(is_admin)
                    self.auth_source = auth_source or 'local'
                
                def check_password(self, password):
                    if self.auth_source == 'ldap' or not self.password_hash:
                        return False
                    return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
                
                def is_authenticated(self):
                    return True
                
                def is_anonymous(self):
                    return False
                
                def get_id(self):
                    return str(self.id)
            
            return DirectUser(*result)
        return None
    except Exception as e:
        logger.error(f"Error in get_user_direct: {e}")
        return None

def authenticate_local_user(username, password):
    """Authenticate user with local credentials"""
    logger.info(f"Attempting local authentication for user: {username}")
    
    # Find user in database
    user = None
    try:
        user = User.query.filter_by(username=username).first()
    except Exception:
        # SQLAlchemy has cached metadata issues, use direct database access
        user = get_user_direct(username)
    
    if not user:
        logger.warning(f"Local user {username} not found")
        return None, "User not found in local database"
    
    if not user.is_active:
        logger.warning(f"Local user {username} is inactive")
        return None, "Account is disabled"
    
    if not user.check_password(password):
        logger.warning(f"Invalid password for local user {username}")
        return None, "Invalid password"
    
    logger.info(f"Local authentication successful for user: {username}")
    return user, "Authentication successful"

def authenticate_ldap_user(username, password):
    """Authenticate user with LDAP/Active Directory"""
    logger.info(f"Attempting LDAP authentication for user: {username}")
    
    if not current_app.config.get('ALLOW_LDAP_AUTH', True):
        return None, "LDAP authentication is disabled"
    
    # Authenticate with LDAP
    ldap_info = ldap_auth.authenticate(username, password)
    if not ldap_info:
        logger.warning(f"LDAP authentication failed for user: {username}")
        return None, "LDAP authentication failed"
    
    logger.info(f"LDAP authentication successful for user: {username}")
    
    # Check if user exists in local database
    user = User.query.filter_by(username=username).first()
    
    if user:
        # Update existing user with LDAP info
        if user.auth_source != 'ldap':
            # Convert local user to LDAP user
            user.auth_source = 'ldap'
            user.password_hash = None  # Clear local password
        
        user.update_from_ldap(ldap_info)
        db.session.commit()
        logger.info(f"Updated existing user {username} with LDAP info")
    else:
        # Create new user from LDAP info
        if not current_app.config.get('AUTO_CREATE_LDAP_USERS', True):
            logger.warning(f"LDAP user {username} not found in local database and auto-creation is disabled")
            return None, "User not found in local database"
        
        user = User.create_from_ldap(ldap_info)
        db.session.add(user)
        db.session.commit()
        logger.info(f"Created new user {username} from LDAP")
    
    return user, "LDAP authentication successful"

def authenticate_user(username, password, auth_method='auto'):
    """
    Authenticate user with specified method or auto-detect
    
    Args:
        username (str): Username
        password (str): Password  
        auth_method (str): 'local', 'ldap', or 'auto'
        
    Returns:
        tuple: (user_object, message)
    """
    
    if auth_method == 'local':
        return authenticate_local_user(username, password)
    elif auth_method == 'ldap':
        return authenticate_ldap_user(username, password)
    elif auth_method == 'auto':
        # Try local first, then LDAP
        if current_app.config.get('ALLOW_LOCAL_AUTH', True):
            user, message = authenticate_local_user(username, password)
            if user:
                return user, message
        
        # If local authentication failed and LDAP is enabled, try LDAP
        if current_app.config.get('ALLOW_LDAP_AUTH', True):
            logger.info(f"Local authentication failed for {username}, trying LDAP...")
            return authenticate_ldap_user(username, password)
        
        return None, "Authentication failed"
    
    return None, "Invalid authentication method"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        auth_method = form.auth_method.data or 'auto'
        
        logger.info(f"Login attempt for user {username} with method {auth_method}")
        
        # Check if user is in whitelist
        current_authorized_users = get_authorized_users()
        if username not in current_authorized_users:
            flash('Access denied. Please contact an administrator if you believe you should have access.', 'error')
            return render_template('auth/login.html', form=form)
        
        # Authenticate user
        user, message = authenticate_user(username, password, auth_method)
        
        if not user:
            flash(f'Authentication failed: {message}', 'error')
            return render_template('auth/login.html', form=form)
        
        if not user.is_active:
            flash(f'Account "{username}" is disabled', 'error')
            return render_template('auth/login.html', form=form)
        
        # Login successful
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        
        # Create success message based on auth method
        auth_source = getattr(user, 'auth_source', 'local')
        if auth_source == 'ldap':
            flash(f'Successfully logged in via LDAP. Welcome {getattr(user, "display_name", username)}!', 'success')
        else:
            flash(f'Successfully logged in. Welcome {username}!', 'success')
        
        logger.info(f"Successful login for user {username} via {auth_source}")
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    auth_source = getattr(current_user, 'auth_source', 'local')
    logout_user()
    flash(f'Successfully logged out. Goodbye {username}!', 'success')
    logger.info(f"User {username} ({auth_source}) logged out")
    return redirect(url_for('auth.login'))

@auth_bp.route('/ldap-test')
@login_required
def ldap_test():
    """Test LDAP connection (admin only)"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    if not current_app.config.get('ALLOW_LDAP_AUTH', True):
        flash('LDAP authentication is disabled', 'warning')
        return redirect(url_for('main.index'))
    
    success, message = ldap_auth.test_connection()
    
    if success:
        flash(f'LDAP Test: {message}', 'success')
    else:
        flash(f'LDAP Test Failed: {message}', 'error')
    
    return redirect(url_for('admin.system_info'))

@auth_bp.route('/create_initial_user')
def create_initial_user():
    """Create initial admin user for testing - remove in production"""
    if User.query.count() == 0:
        admin_user = User(username='admin', auth_source='local')
        admin_user.set_password('admin123')  # Change this in production
        admin_user.is_admin = True
        db.session.add(admin_user)
        db.session.commit()
        flash('Initial admin user created successfully', 'success')
    else:
        flash('Users already exist', 'warning')
    return redirect(url_for('auth.login'))