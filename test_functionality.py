#!/usr/bin/env python3
"""
Basic functionality test for CARPEM Oncocentre
"""

import os
from app import create_app
from models import db, User, Patient

def test_app_creation():
    """Test that the app can be created and configured"""
    try:
        # Set environment variables for authorization
        os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
        
        app = create_app()
        
        print("SUCCESS: Application created successfully")
        print(f"  - Debug mode: {app.config.get('DEBUG', False)}")
        print(f"  - CSRF enabled: {app.config.get('WTF_CSRF_ENABLED', True)}")
        print(f"  - Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        return True
    except Exception as e:
        print(f"ERROR: Error creating application: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    try:
        app = create_app()
        
        with app.app_context():
            # Test user creation
            test_user = User(username='testfunc')
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
            
            # Test user retrieval
            retrieved_user = User.query.filter_by(username='testfunc').first()
            assert retrieved_user is not None
            assert retrieved_user.check_password('testpass123')
            
            # Test patient creation with encryption
            patient = Patient(
                oncocentre_id='ONCOCENTRE_2025_99999',
                sex='M',
                created_by=retrieved_user.id
            )
            patient.ipp = 'TEST123456'
            patient.first_name = 'TestName'
            patient.last_name = 'TestLast'
            patient.birth_date = '1990-01-01'
            
            db.session.add(patient)
            db.session.commit()
            
            # Test encryption/decryption
            retrieved_patient = Patient.query.filter_by(oncocentre_id='ONCOCENTRE_2025_99999').first()
            assert retrieved_patient is not None
            assert retrieved_patient.ipp == 'TEST123456'
            assert retrieved_patient.first_name == 'TestName'
            assert retrieved_patient.last_name == 'TestLast'
            
            # Verify data is encrypted in database
            assert retrieved_patient.ipp_encrypted != 'TEST123456'
            assert retrieved_patient.first_name_encrypted != 'TestName'
            assert retrieved_patient.last_name_encrypted != 'TestLast'
            
            print("SUCCESS: Database operations successful")
            print("  - User creation and authentication: OK")
            print("  - Patient creation with encryption: OK")
            print("  - Data encryption/decryption: OK")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Error in database operations: {e}")
        return False

def test_routes_accessibility():
    """Test that routes are properly configured"""
    try:
        app = create_app()
        client = app.test_client()
        
        # Test that protected routes redirect to login
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
        
        response = client.get('/patients')
        assert response.status_code == 302  # Redirect to login
        
        # Test that login page is accessible
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        print("SUCCESS: Route accessibility tests passed")
        print("  - Protected routes require authentication: OK")
        print("  - Login page accessible: OK")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error in route testing: {e}")
        return False

def test_encryption_key_management():
    """Test encryption key management"""
    try:
        from models import get_encryption_key, ENCRYPTION_KEY
        
        # Test key exists
        assert ENCRYPTION_KEY is not None
        assert len(ENCRYPTION_KEY) > 0
        
        # Test key file exists
        assert os.path.exists('encryption.key')
        
        print("SUCCESS: Encryption key management working")
        print("  - Encryption key generated: OK")
        print("  - Key file created: OK")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error in encryption key management: {e}")
        return False

def main():
    """Run all functionality tests"""
    print("CARPEM Oncocentre - Functionality Test")
    print("=" * 40)
    
    tests = [
        ("Application Creation", test_app_creation),
        ("Database Operations", test_database_operations),
        ("Route Accessibility", test_routes_accessibility),
        ("Encryption Key Management", test_encryption_key_management)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed!")
    
    print(f"\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All functionality tests PASSED!")
        print("\nNext steps:")
        print("  1. Set AUTHORIZED_USERS environment variable:")
        print("     export AUTHORIZED_USERS=\"admin,user1,user2,doctor1,researcher1\"")
        print("  2. Start the secure HTTPS server:")
        print("     python run_https.py")
        print("  3. Access application at: https://localhost:5000")
        print("  4. Login with test credentials (see create_test_users.py output)")
        return True
    else:
        print(f"FAILED: {total - passed} tests FAILED!")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)