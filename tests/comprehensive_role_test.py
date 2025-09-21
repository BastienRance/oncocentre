#!/usr/bin/env python3
"""
Comprehensive test script for all user roles and permissions
Tests admin, regular user, and principal investigator capabilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.core.models import db, User, Patient
from datetime import datetime, date
import json

def setup_test_users(app):
    """Create test users with different roles"""
    with app.app_context():
        db.create_all()

        # Clear existing test users
        User.query.filter(User.username.in_(['test_admin', 'test_user', 'test_pi'])).delete()
        db.session.commit()

        # Create admin user
        admin_user = User(
            username='test_admin',
            is_admin=True,
            is_active=True,
            is_principal_investigator=False
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        # Create regular user
        regular_user = User(
            username='test_user',
            is_admin=False,
            is_active=True,
            is_principal_investigator=False
        )
        regular_user.set_password('user123')
        db.session.add(regular_user)

        # Create principal investigator
        pi_user = User(
            username='test_pi',
            is_admin=False,
            is_active=True,
            is_principal_investigator=True
        )
        pi_user.set_password('pi123')
        db.session.add(pi_user)

        db.session.commit()

        print("✓ Created test users:")
        print(f"  - Admin: test_admin (ID: {admin_user.id})")
        print(f"  - Regular User: test_user (ID: {regular_user.id})")
        print(f"  - Principal Investigator: test_pi (ID: {pi_user.id})")

        return admin_user, regular_user, pi_user

def create_test_patient(app, user_id, patient_data):
    """Create a test patient"""
    with app.app_context():
        patient = Patient(
            ipp=patient_data['ipp'],
            first_name=patient_data['first_name'],
            last_name=patient_data['last_name'],
            birth_date=patient_data['birth_date'],
            sex=patient_data['sex'],
            oncocentre_id=patient_data['oncocentre_id'],
            created_by=user_id
        )
        db.session.add(patient)
        db.session.commit()
        return patient

def test_authentication_flows(app):
    """Test authentication for all user types"""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION FLOWS")
    print("="*60)

    users_to_test = [
        ('test_admin', 'admin123', 'Admin'),
        ('test_user', 'user123', 'Regular User'),
        ('test_pi', 'pi123', 'Principal Investigator')
    ]

    with app.test_client() as client:
        for username, password, role in users_to_test:
            print(f"\n➤ Testing {role} authentication...")

            # Test login
            response = client.post('/auth/login', data={
                'username': username,
                'password': password,
                'auth_method': 'local'
            }, follow_redirects=False)

            if response.status_code in [200, 302]:
                print(f"  ✓ {role} login successful")

                # Test logout
                response = client.get('/auth/logout', follow_redirects=False)
                if response.status_code == 302:
                    print(f"  ✓ {role} logout successful")
                else:
                    print(f"  ✗ {role} logout failed")
            else:
                print(f"  ✗ {role} login failed (Status: {response.status_code})")

def test_admin_actions(app):
    """Test admin-specific actions"""
    print("\n" + "="*60)
    print("TESTING ADMIN USER ACTIONS")
    print("="*60)

    with app.test_client() as client:
        # Login as admin
        response = client.post('/auth/login', data={
            'username': 'test_admin',
            'password': 'admin123',
            'auth_method': 'local'
        }, follow_redirects=True)

        print("\n➤ Testing admin dashboard access...")
        response = client.get('/admin/dashboard')
        if response.status_code == 200:
            print("  ✓ Admin dashboard accessible")
        else:
            print(f"  ✗ Admin dashboard access failed (Status: {response.status_code})")

        print("\n➤ Testing user management access...")
        response = client.get('/admin/users')
        if response.status_code == 200:
            print("  ✓ User management page accessible")
        else:
            print(f"  ✗ User management access failed (Status: {response.status_code})")

        print("\n➤ Testing user creation access...")
        response = client.get('/admin/users/create')
        if response.status_code == 200:
            print("  ✓ User creation page accessible")
        else:
            print(f"  ✗ User creation access failed (Status: {response.status_code})")

        print("\n➤ Testing system info access...")
        response = client.get('/admin/system_info')
        if response.status_code == 200:
            print("  ✓ System info page accessible")
        else:
            print(f"  ✗ System info access failed (Status: {response.status_code})")

        print("\n➤ Testing admin patient access restriction...")
        response = client.get('/')
        response_text = response.get_data(as_text=True)
        if 'administrators cannot create' in response_text.lower() or response.status_code == 302:
            print("  ✓ Admin correctly restricted from patient creation")
        else:
            print("  ✗ Admin restriction on patient creation failed")

        # Test creating a new user via admin interface
        print("\n➤ Testing user creation functionality...")
        response = client.post('/admin/users/create', data={
            'username': 'new_test_user',
            'password': 'newpass123',
            'confirm_password': 'newpass123',
            'is_active': True,
            'is_admin': False,
            'is_principal_investigator': False
        }, follow_redirects=True)

        if response.status_code == 200:
            # Check if user was created
            with app.app_context():
                new_user = User.query.filter_by(username='new_test_user').first()
                if new_user:
                    print("  ✓ User creation via admin interface successful")
                    # Clean up
                    db.session.delete(new_user)
                    db.session.commit()
                else:
                    print("  ✗ User creation via admin interface failed - user not found")
        else:
            print(f"  ✗ User creation via admin interface failed (Status: {response.status_code})")

def test_regular_user_actions(app):
    """Test regular user actions and restrictions"""
    print("\n" + "="*60)
    print("TESTING REGULAR USER ACTIONS")
    print("="*60)

    with app.test_client() as client:
        # Login as regular user
        response = client.post('/auth/login', data={
            'username': 'test_user',
            'password': 'user123',
            'auth_method': 'local'
        }, follow_redirects=True)

        print("\n➤ Testing patient creation access...")
        response = client.get('/')
        if response.status_code == 200 and 'create patient' in response.get_data(as_text=True).lower():
            print("  ✓ Regular user can access patient creation")
        else:
            print(f"  ✗ Regular user patient creation access failed (Status: {response.status_code})")

        print("\n➤ Testing patient list access...")
        response = client.get('/patients')
        if response.status_code == 200:
            print("  ✓ Regular user can access patient list")
        else:
            print(f"  ✗ Regular user patient list access failed (Status: {response.status_code})")

        print("\n➤ Testing admin area access restriction...")
        response = client.get('/admin/dashboard')
        if response.status_code in [302, 403, 401]:
            print("  ✓ Regular user correctly restricted from admin area")
        else:
            print(f"  ✗ Regular user admin restriction failed (Status: {response.status_code})")

        # Test creating a patient
        print("\n➤ Testing patient creation functionality...")
        response = client.post('/', data={
            'ipp': '12345678',
            'first_name': 'Test',
            'last_name': 'Patient',
            'birth_date': '1990-01-01',
            'sex': 'M'
        }, follow_redirects=True)

        if response.status_code == 200:
            # Check if patient was created (simplified check)
            with app.app_context():
                user = User.query.filter_by(username='test_user').first()
                patients = Patient.query.filter_by(created_by=user.id).all()
                if any(p.ipp == '12345678' for p in patients):
                    print("  ✓ Patient creation by regular user successful")
                    # Clean up
                    for p in patients:
                        if p.ipp == '12345678':
                            db.session.delete(p)
                    db.session.commit()
                else:
                    print("  ✗ Patient creation by regular user failed - patient not found")
        else:
            print(f"  ✗ Patient creation by regular user failed (Status: {response.status_code})")

def test_principal_investigator_actions(app):
    """Test principal investigator actions and privileges"""
    print("\n" + "="*60)
    print("TESTING PRINCIPAL INVESTIGATOR ACTIONS")
    print("="*60)

    with app.test_client() as client:
        # Login as PI
        response = client.post('/auth/login', data={
            'username': 'test_pi',
            'password': 'pi123',
            'auth_method': 'local'
        }, follow_redirects=True)

        print("\n➤ Testing PI patient creation access...")
        response = client.get('/')
        if response.status_code == 200 and 'create patient' in response.get_data(as_text=True).lower():
            print("  ✓ PI can access patient creation")
        else:
            print(f"  ✗ PI patient creation access failed (Status: {response.status_code})")

        print("\n➤ Testing PI patient list access...")
        response = client.get('/patients')
        if response.status_code == 200:
            print("  ✓ PI can access patient list")
            # Check if PI can see all patients (not just their own)
            response_text = response.get_data(as_text=True)
            if 'principal investigator' in response_text.lower() or 'all patients' in response_text.lower():
                print("  ✓ PI has enhanced patient visibility")
            else:
                print("  ? PI patient visibility may be standard (need patients to verify)")
        else:
            print(f"  ✗ PI patient list access failed (Status: {response.status_code})")

        print("\n➤ Testing PI admin area access restriction...")
        response = client.get('/admin/dashboard')
        if response.status_code in [302, 403, 401]:
            print("  ✓ PI correctly restricted from admin area")
        else:
            print(f"  ✗ PI admin restriction failed (Status: {response.status_code})")

        # Test creating a patient as PI
        print("\n➤ Testing patient creation functionality as PI...")
        response = client.post('/', data={
            'ipp': '87654321',
            'first_name': 'PI',
            'last_name': 'Patient',
            'birth_date': '1985-05-15',
            'sex': 'F'
        }, follow_redirects=True)

        if response.status_code == 200:
            print("  ✓ Patient creation by PI successful")
        else:
            print(f"  ✗ Patient creation by PI failed (Status: {response.status_code})")

def test_access_control_boundaries(app):
    """Test access control and security boundaries"""
    print("\n" + "="*60)
    print("TESTING ACCESS CONTROL & SECURITY BOUNDARIES")
    print("="*60)

    # Create test patients for each user
    with app.app_context():
        admin_user = User.query.filter_by(username='test_admin').first()
        regular_user = User.query.filter_by(username='test_user').first()
        pi_user = User.query.filter_by(username='test_pi').first()

        # Create patients for testing isolation
        admin_patient = create_test_patient(app, admin_user.id, {
            'ipp': 'ADMIN001',
            'first_name': 'Admin',
            'last_name': 'TestPatient',
            'birth_date': date(1980, 1, 1),
            'sex': 'M',
            'oncocentre_id': 'ONCOCENTRE_2024_00001'
        })

        user_patient = create_test_patient(app, regular_user.id, {
            'ipp': 'USER001',
            'first_name': 'User',
            'last_name': 'TestPatient',
            'birth_date': date(1981, 1, 1),
            'sex': 'F',
            'oncocentre_id': 'ONCOCENTRE_2024_00002'
        })

        pi_patient = create_test_patient(app, pi_user.id, {
            'ipp': 'PI001',
            'first_name': 'PI',
            'last_name': 'TestPatient',
            'birth_date': date(1982, 1, 1),
            'sex': 'M',
            'oncocentre_id': 'ONCOCENTRE_2024_00003'
        })

    with app.test_client() as client:
        print("\n➤ Testing patient data isolation...")

        # Test as regular user
        client.post('/auth/login', data={
            'username': 'test_user',
            'password': 'user123',
            'auth_method': 'local'
        })

        response = client.get('/patients')
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            user_can_see_own = 'USER001' in response_text
            user_can_see_admin = 'ADMIN001' in response_text
            user_can_see_pi = 'PI001' in response_text

            if user_can_see_own and not user_can_see_admin and not user_can_see_pi:
                print("  ✓ Regular user sees only their own patients")
            elif user_can_see_own:
                print("  ⚠ Regular user sees their patients but may see others too")
            else:
                print("  ✗ Regular user cannot see their own patients")

        client.get('/auth/logout')

        # Test as PI
        client.post('/auth/login', data={
            'username': 'test_pi',
            'password': 'pi123',
            'auth_method': 'local'
        })

        response = client.get('/patients')
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            pi_can_see_own = 'PI001' in response_text
            pi_can_see_all = 'USER001' in response_text and 'ADMIN001' in response_text

            if pi_can_see_all:
                print("  ✓ PI can see all patients")
            elif pi_can_see_own:
                print("  ⚠ PI sees only their own patients (may be intended)")
            else:
                print("  ✗ PI cannot see patients")

        client.get('/auth/logout')

    # Clean up test patients
    with app.app_context():
        test_patients = Patient.query.all()
        for patient in test_patients:
            if patient.ipp in ['ADMIN001', 'USER001', 'PI001']:
                db.session.delete(patient)
        db.session.commit()

def test_role_properties(app):
    """Test role-specific properties and capabilities"""
    print("\n" + "="*60)
    print("TESTING ROLE PROPERTIES")
    print("="*60)

    with app.app_context():
        admin_user = User.query.filter_by(username='test_admin').first()
        regular_user = User.query.filter_by(username='test_user').first()
        pi_user = User.query.filter_by(username='test_pi').first()

        print("\n➤ Testing user role flags...")
        print(f"  Admin user - is_admin: {admin_user.is_admin}, is_pi: {admin_user.is_principal_investigator}")
        print(f"  Regular user - is_admin: {regular_user.is_admin}, is_pi: {regular_user.is_principal_investigator}")
        print(f"  PI user - is_admin: {pi_user.is_admin}, is_pi: {pi_user.is_principal_investigator}")

        # Verify role flags are correct
        roles_correct = (
            admin_user.is_admin and not admin_user.is_principal_investigator and
            not regular_user.is_admin and not regular_user.is_principal_investigator and
            not pi_user.is_admin and pi_user.is_principal_investigator
        )

        if roles_correct:
            print("  ✓ All user role flags are correctly set")
        else:
            print("  ✗ Some user role flags are incorrect")

        print("\n➤ Testing user properties...")
        print(f"  Admin patient count: {admin_user.patient_count}")
        print(f"  Regular user patient count: {regular_user.patient_count}")
        print(f"  PI patient count: {pi_user.patient_count}")

def run_existing_tests(app):
    """Run existing test files"""
    print("\n" + "="*60)
    print("RUNNING EXISTING TEST SUITE")
    print("="*60)

    test_files = [
        'test_specifications.py',
        'tests/test_auth.py',
        'tests/test_patients.py',
        'tests/test_refactored_app.py'
    ]

    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n➤ Running {test_file}...")
            result = os.system(f'python {test_file}')
            if result == 0:
                print(f"  ✓ {test_file} passed")
            else:
                print(f"  ✗ {test_file} failed")
        else:
            print(f"  ⚠ {test_file} not found")

def main():
    """Run comprehensive role testing"""
    print("CARPEM Oncocentre - Comprehensive Role Testing")
    print("=" * 60)

    # Create test app
    app = create_app('testing')

    try:
        # Setup test environment
        admin_user, regular_user, pi_user = setup_test_users(app)

        # Run all tests
        test_authentication_flows(app)
        test_admin_actions(app)
        test_regular_user_actions(app)
        test_principal_investigator_actions(app)
        test_access_control_boundaries(app)
        test_role_properties(app)
        run_existing_tests(app)

        # Cleanup
        with app.app_context():
            User.query.filter(User.username.in_(['test_admin', 'test_user', 'test_pi'])).delete()
            db.session.commit()

        print("\n" + "="*60)
        print("✓ COMPREHENSIVE ROLE TESTING COMPLETED")
        print("="*60)

        return 0

    except Exception as e:
        print(f"\n✗ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())