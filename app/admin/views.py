"""
Administrative routes for user management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from ..core.models import User, Patient, db
from .forms import CreateUserForm, EditUserForm

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system statistics"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    pi_users = User.query.filter_by(is_principal_investigator=True).count()
    total_patients = Patient.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'pi_users': pi_users,
        'total_patients': total_patients,
        'recent_users': recent_users
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user"""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            is_admin=form.is_admin.data,
            is_principal_investigator=form.is_principal_investigator.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'User "{user.username}" created successfully!', 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        user.is_active = form.is_active.data
        user.is_admin = form.is_admin.data
        user.is_principal_investigator = form.is_principal_investigator.data
        
        if form.reset_password.data:
            user.set_password(form.reset_password.data)
        
        try:
            db.session.commit()
            flash(f'User "{user.username}" updated successfully!', 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
    else:
        # Pre-populate form with current values
        form.is_active.data = user.is_active
        form.is_admin.data = user.is_admin
        form.is_principal_investigator.data = user.is_principal_investigator
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete or deactivate a user"""
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.list_users'))
    
    # Check if user has patients
    patient_count = Patient.query.filter_by(created_by=user.id).count()
    
    if patient_count > 0:
        # Deactivate instead of delete
        user.is_active = False
        db.session.commit()
        flash(f'User "{user.username}" deactivated (has {patient_count} patients)', 'warning')
    else:
        # Safe to delete
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" deleted successfully!', 'success')
    
    return redirect(url_for('admin.list_users'))

# System info page removed as per specification