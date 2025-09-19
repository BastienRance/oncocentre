#!/usr/bin/env python3
"""
Patient management tests for the CARPEM Oncocentre application
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import db, User, Patient
from datetime import date

def test_patient_creation():
    """Test direct patient creation through models"""
    print("🧪 Testing Patient Creation")
    print("=" * 30)
    
    app = create_app('testing')
    
    with app.app_context():
        # Create test user
        user = User(username='testuser')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Test patient creation
        from app.utils import generate_oncocentre_id
        
        oncocentre_id = generate_oncocentre_id()
        
        patient = Patient(
            oncocentre_id=oncocentre_id,
            sex='M',
            created_by=user.id
        )
        
        # Set encrypted fields
        patient.ipp = 'TEST123'
        patient.first_name = 'Test'
        patient.last_name = 'Patient'
        patient.birth_date = date(1990, 1, 1)
        
        try:
            db.session.add(patient)
            db.session.commit()
            
            # Verify data
            retrieved = Patient.query.first()
            
            if retrieved.ipp == 'TEST123':
                print("✅ Patient encryption/decryption working")
                return True
            else:
                print("❌ Patient data mismatch")
                return False
                
        except Exception as e:
            print(f"❌ Patient creation failed: {e}")
            return False

def test_patient_validation():
    """Test patient data validation"""
    print("🧪 Testing Patient Validation")
    print("=" * 30)
    
    from app.utils import validate_patient_data
    
    # Test valid data
    errors = validate_patient_data('IPP123', 'John', 'Doe', date(1990, 1, 1), 'M')
    if len(errors) == 0:
        print("✅ Valid patient data accepted")
    else:
        print(f"❌ Valid data rejected: {errors}")
        return False
    
    # Test invalid data
    errors = validate_patient_data('', '', '', None, 'X')
    if len(errors) > 0:
        print("✅ Invalid patient data rejected")
        return True
    else:
        print("❌ Invalid data accepted")
        return False

if __name__ == "__main__":
    print("🧪 CARPEM Oncocentre Patient Tests")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test patient validation
    total_tests += 1
    if test_patient_validation():
        tests_passed += 1
    
    # Test patient creation
    total_tests += 1
    if test_patient_creation():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All patient tests passed!")
        sys.exit(0)
    else:
        print("❌ Some patient tests failed!")
        sys.exit(1)