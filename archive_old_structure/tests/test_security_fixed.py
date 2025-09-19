#!/usr/bin/env python3
"""
Fixed Security Test Suite for CARPEM Oncocentre
"""

import unittest
import tempfile
import os
from app import create_app
from models import db, User, Patient
from datetime import datetime, date

class SecurityTestCase(unittest.TestCase):
    """Base class for security tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test users within app context
            self.test_user = User(username='testuser')
            self.test_user.set_password('testpass123')
            db.session.add(self.test_user)
            
            self.other_user = User(username='otheruser')
            self.other_user.set_password('otherpass123')
            db.session.add(self.other_user)
            
            db.session.commit()
            
            # Store user IDs for later use
            self.test_user_id = self.test_user.id
            self.other_user_id = self.other_user.id
    
    def tearDown(self):
        """Clean up test environment"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def login(self, username, password):
        """Helper method to login"""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

class BasicSecurityTests(SecurityTestCase):
    """Test basic security functionality"""
    
    def test_login_required_for_main_pages(self):
        """Test that main pages require login"""
        # Test main page
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
        
        # Test patients list
        rv = self.client.get('/patients')
        self.assertEqual(rv.status_code, 302)  # Redirect to login
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            # Password should not be stored in plaintext
            self.assertNotEqual(user.password_hash, 'testpass123')
            # But should validate correctly
            self.assertTrue(user.check_password('testpass123'))
            self.assertFalse(user.check_password('wrongpass'))
    
    def test_patient_data_encryption(self):
        """Test that sensitive patient data is encrypted"""
        with self.app.app_context():
            # Create a patient using stored user ID
            patient = Patient(
                oncocentre_id='ONCOCENTRE_2025_00001',
                sex='M',
                created_by=self.test_user_id
            )
            patient.ipp = 'IPP123456'
            patient.first_name = 'John'
            patient.last_name = 'Doe'
            patient.birth_date = date(1990, 1, 1)
            
            db.session.add(patient)
            db.session.commit()
            
            # Check that encrypted fields are different from original
            self.assertNotEqual(patient.ipp_encrypted, 'IPP123456')
            self.assertNotEqual(patient.first_name_encrypted, 'John')
            self.assertNotEqual(patient.last_name_encrypted, 'Doe')
            
            # But decrypted values should match
            self.assertEqual(patient.ipp, 'IPP123456')
            self.assertEqual(patient.first_name, 'John')
            self.assertEqual(patient.last_name, 'Doe')
            self.assertEqual(patient.birth_date, date(1990, 1, 1))
    
    def test_authentication_workflow(self):
        """Test complete authentication workflow"""
        with self.app.app_context():
            # Mock authorized users for this test
            import auth
            auth.AUTHORIZED_USERS.add('testuser')
            
            # Test invalid login
            rv = self.login('testuser', 'wrongpass')
            self.assertIn(b'incorrect', rv.data)
            
            # Test valid login
            rv = self.login('testuser', 'testpass123')
            self.assertIn(b'Connexion r\xc3\xa9ussie', rv.data)
    
    def test_user_access_control(self):
        """Test that users can only access their own data"""
        with self.app.app_context():
            # Create patients for different users
            patient1 = Patient(
                oncocentre_id='ONCOCENTRE_2025_00001',
                sex='M',
                created_by=self.test_user_id
            )
            patient1.ipp = 'IPP123456'
            patient1.first_name = 'John'
            patient1.last_name = 'Doe'
            patient1.birth_date = date(1990, 1, 1)
            
            patient2 = Patient(
                oncocentre_id='ONCOCENTRE_2025_00002',
                sex='F',
                created_by=self.other_user_id
            )
            patient2.ipp = 'IPP789012'
            patient2.first_name = 'Jane'
            patient2.last_name = 'Smith'
            patient2.birth_date = date(1985, 5, 15)
            
            db.session.add(patient1)
            db.session.add(patient2)
            db.session.commit()
            
            # Mock authorized users
            import auth
            auth.AUTHORIZED_USERS.update(['testuser', 'otheruser'])
            
            # Login as first user
            self.login('testuser', 'testpass123')
            rv = self.client.get('/patients')
            
            # Should see own patient but not other user's patient
            self.assertIn(b'ONCOCENTRE_2025_00001', rv.data)
            self.assertNotIn(b'ONCOCENTRE_2025_00002', rv.data)
    
    def test_encryption_key_generation(self):
        """Test that encryption key is properly generated"""
        from models import ENCRYPTION_KEY
        
        # Key should be generated
        self.assertIsNotNone(ENCRYPTION_KEY)
        self.assertTrue(len(ENCRYPTION_KEY) > 0)
    
    def test_form_validation(self):
        """Test basic form validation"""
        from forms import PatientForm
        
        with self.app.app_context():
            # Test empty form
            form = PatientForm(data={})
            self.assertFalse(form.validate())
            
            # Test valid form
            form = PatientForm(data={
                'ipp': 'IPP123456',
                'first_name': 'John',
                'last_name': 'Doe',
                'birth_date': date(1990, 1, 1),
                'sex': 'M'
            })
            self.assertTrue(form.validate())

def run_basic_security_tests():
    """Run basic security tests"""
    print("Running CARPEM Oncocentre Basic Security Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(BasicSecurityTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_basic_security_tests()
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)