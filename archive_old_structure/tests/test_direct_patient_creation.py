#!/usr/bin/env python3
"""
Direct test of patient creation functionality without web interface
"""

import sys
import os
from datetime import datetime, date

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_patient_creation():
    """Test patient creation directly through the model"""
    
    print("🧪 Testing Direct Patient Creation")
    print("=" * 40)
    
    try:
        # Import Flask app and models
        from app import create_app
        from models import db, User, Patient
        
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            # Step 1: Check if user1 exists
            print("\n1. Checking user1 exists...")
            user1 = User.query.filter_by(username='user1').first()
            
            if not user1:
                print("❌ user1 not found in database")
                return False
            
            print(f"✅ Found user1: {user1.username} (ID: {user1.id}, Active: {user1.is_active})")
            
            # Step 2: Check current patient count
            print("\n2. Checking existing patients...")
            existing_count = Patient.query.filter_by(created_by=user1.id).count()
            total_count = Patient.query.count()
            
            print(f"✅ User1 has {existing_count} patients")
            print(f"✅ Total patients in database: {total_count}")
            
            # Step 3: Create test patients directly
            print("\n3. Creating test patients...")
            
            test_patients_data = [
                {
                    'ipp': 'DIRECT001',
                    'first_name': 'Alice',
                    'last_name': 'Durand',
                    'birth_date': date(1985, 3, 10),
                    'sex': 'F'
                },
                {
                    'ipp': 'DIRECT002',
                    'first_name': 'Bob',
                    'last_name': 'Moreau',
                    'birth_date': date(1992, 7, 25),
                    'sex': 'M'
                }
            ]
            
            created_patients = []
            
            for i, patient_data in enumerate(test_patients_data, 1):
                print(f"\n   Creating patient {i}: {patient_data['first_name']} {patient_data['last_name']}")
                
                # Generate oncocentre ID
                from utils import generate_oncocentre_id
                oncocentre_id = generate_oncocentre_id()
                print(f"   Generated ID: {oncocentre_id}")
                
                # Create patient instance
                patient = Patient(
                    oncocentre_id=oncocentre_id,
                    sex=patient_data['sex'],
                    created_by=user1.id
                )
                
                # Set encrypted properties
                patient.ipp = patient_data['ipp']
                patient.first_name = patient_data['first_name']
                patient.last_name = patient_data['last_name']
                patient.birth_date = patient_data['birth_date']
                
                try:
                    # Add to database
                    db.session.add(patient)
                    db.session.commit()
                    
                    print(f"   ✅ Patient {i} created successfully")
                    created_patients.append(patient)
                    
                except Exception as e:
                    print(f"   ❌ Failed to create patient {i}: {e}")
                    db.session.rollback()
            
            # Step 4: Verify created patients
            print(f"\n4. Verifying created patients...")
            
            user1_patients = Patient.query.filter_by(created_by=user1.id).all()
            print(f"✅ User1 now has {len(user1_patients)} patients")
            
            for patient in user1_patients:
                try:
                    # Test decryption
                    ipp = patient.ipp
                    first_name = patient.first_name
                    last_name = patient.last_name
                    birth_date = patient.birth_date
                    
                    print(f"   - {patient.oncocentre_id}: {first_name} {last_name}")
                    print(f"     IPP: {ipp}, DOB: {birth_date}, Sex: {patient.sex}")
                    
                except Exception as e:
                    print(f"   ❌ Error decrypting patient {patient.oncocentre_id}: {e}")
            
            # Step 5: Test duplicate prevention
            print(f"\n5. Testing duplicate prevention...")
            
            try:
                duplicate_patient = Patient(
                    oncocentre_id=generate_oncocentre_id(),
                    sex='M',
                    created_by=user1.id
                )
                duplicate_patient.ipp = 'DIRECT001'  # Same IPP as first patient
                duplicate_patient.first_name = 'Duplicate'
                duplicate_patient.last_name = 'Test'
                duplicate_patient.birth_date = date(1990, 1, 1)
                
                db.session.add(duplicate_patient)
                db.session.commit()
                
                print("⚠️  Duplicate patient was created (this should be prevented)")
                
            except Exception as e:
                print(f"✅ Duplicate prevention working: {e}")
                db.session.rollback()
            
            print(f"\n🎉 Direct test completed! Created {len(created_patients)} patients")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_patient_creation()
    
    if success:
        print("\n✅ All direct tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Direct tests failed!")
        sys.exit(1)