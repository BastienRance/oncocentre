"""
Main application routes for patient management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..core.models import Patient, db
from ..core import generate_oncocentre_id, validate_patient_data
from .forms import PatientForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Main page with patient identifier creation form"""
    # Admins cannot create patients
    if current_user.is_admin:
        flash('Administrators cannot create patient identifiers. Please use a regular user account.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    form = PatientForm()
    return render_template('main/index.html', form=form)

@main_bp.route('/preview_id', methods=['POST'])
@login_required
def preview_id():
    """AJAX endpoint to preview the next oncocentre ID"""
    try:
        next_id = generate_oncocentre_id()
        return jsonify({'oncocentre_id': next_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/create_patient', methods=['POST'])
@login_required
def create_patient():
    """Create a new patient with oncocentre identifier"""
    # Admins cannot create patients
    if current_user.is_admin:
        flash('Administrators cannot create patient identifiers.', 'error')
        return redirect(url_for('admin.dashboard'))
        
    form = PatientForm()
    
    if form.validate_on_submit():
        ipp = form.ipp.data.strip()
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        birth_date = form.birth_date.data
        sex = form.sex.data
        
        # Check if patient with same IPP already exists for this user
        existing_patient = Patient.query.filter_by(created_by=current_user.id).filter(
            Patient.ipp_encrypted.like('%' + ipp + '%')
        ).first()
        
        if existing_patient and existing_patient.ipp == ipp:
            flash(f'Patient with IPP {ipp} already exists with ID {existing_patient.oncocentre_id}', 'warning')
            return redirect(url_for('main.index'))
        
        # Generate oncocentre ID and create patient
        oncocentre_id = generate_oncocentre_id()
        
        patient = Patient(
            oncocentre_id=oncocentre_id,
            sex=sex,
            created_by=current_user.id
        )
        
        # Set encrypted fields using properties
        patient.ipp = ipp
        patient.first_name = first_name
        patient.last_name = last_name
        patient.birth_date = birth_date
        
        try:
            db.session.add(patient)
            db.session.commit()
            flash(f'Patient created successfully with ID: {oncocentre_id}', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating patient: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('main.index'))

@main_bp.route('/patients')
@login_required
def list_patients():
    """List patients - all for principal investigators, own for users, none for admins"""
    # Admins cannot view patients
    if current_user.is_admin and not current_user.is_principal_investigator:
        flash('Administrators cannot view patient lists. Please use a regular user account.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    # Principal investigators see all patients
    if current_user.is_principal_investigator:
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
    else:
        # Regular users see only their own patients
        patients = Patient.query.filter_by(created_by=current_user.id).order_by(Patient.created_at.desc()).all()
    
    return render_template('main/patients.html', patients=patients, is_pi=current_user.is_principal_investigator)