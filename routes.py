from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models import Patient, db
from utils import generate_oncocentre_id, validate_patient_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main page with patient identifier creation form"""
    return render_template('index.html')

@main_bp.route('/preview_id', methods=['POST'])
def preview_id():
    """AJAX endpoint to preview the next oncocentre ID"""
    try:
        next_id = generate_oncocentre_id()
        return jsonify({'oncocentre_id': next_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/create_patient', methods=['POST'])
def create_patient():
    """Create a new patient with oncocentre identifier"""
    ipp = request.form.get('ipp', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    birth_date_str = request.form.get('birth_date', '')
    sex = request.form.get('sex', '')
    
    # Validate input
    errors = validate_patient_data(ipp, first_name, last_name, birth_date_str, sex)
    
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Invalid birth date format")
    else:
        birth_date = None
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('main.index'))
    
    # Check if patient with same IPP already exists
    existing_patient = Patient.query.filter_by(ipp=ipp).first()
    if existing_patient:
        flash(f'Patient with IPP {ipp} already exists with ID {existing_patient.oncocentre_id}', 'warning')
        return redirect(url_for('main.index'))
    
    # Generate oncocentre ID and create patient
    oncocentre_id = generate_oncocentre_id()
    
    patient = Patient(
        ipp=ipp,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        sex=sex,
        oncocentre_id=oncocentre_id
    )
    
    try:
        db.session.add(patient)
        db.session.commit()
        flash(f'Patient created successfully with ID: {oncocentre_id}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating patient: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

@main_bp.route('/patients')
def list_patients():
    """List all patients in the study"""
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('patients.html', patients=patients)