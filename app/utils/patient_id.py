"""
Patient identifier generation utilities
"""

from datetime import datetime

def generate_oncocentre_id():
    """Generate the next ONCOCENTRE identifier following the format ONCOCENTRE_YYYY_NNNNN"""
    from app.models import Patient
    
    current_year = datetime.now().year
    
    # Find the highest sequence number for the current year
    last_patient = Patient.query.filter(
        Patient.oncocentre_id.like(f'ONCOCENTRE_{current_year}_%')
    ).order_by(Patient.id.desc()).first()
    
    if last_patient:
        # Extract sequence number from the last ID
        last_id_parts = last_patient.oncocentre_id.split('_')
        if len(last_id_parts) == 3:
            try:
                last_sequence = int(last_id_parts[2])
                next_sequence = last_sequence + 1
            except ValueError:
                next_sequence = 1
        else:
            next_sequence = 1
    else:
        next_sequence = 1
    
    # Format with zero padding
    return f"ONCOCENTRE_{current_year}_{next_sequence:05d}"

def validate_patient_data(ipp, first_name, last_name, birth_date, sex):
    """Validate patient data before creating identifier"""
    errors = []
    
    if not ipp or not ipp.strip():
        errors.append("IPP is required")
    
    if not first_name or not first_name.strip():
        errors.append("First name is required")
    
    if not last_name or not last_name.strip():
        errors.append("Last name is required")
    
    if not birth_date:
        errors.append("Birth date is required")
    
    if sex not in ['M', 'F']:
        errors.append("Sex must be M or F")
    
    return errors