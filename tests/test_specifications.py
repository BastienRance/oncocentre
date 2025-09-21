#!/usr/bin/env python3
"""
Test script to verify the specification updates have been implemented correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.core.models import db, User

def test_principal_investigator_role():
    """Test that principal investigator role has been added"""
    print("Testing principal investigator role...")
    
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        
        # Test creating a user with PI role
        pi_user = User(username='testpi', is_principal_investigator=True)
        pi_user.set_password('testpass')
        db.session.add(pi_user)
        db.session.commit()
        
        # Verify the role
        retrieved_user = User.query.filter_by(username='testpi').first()
        if retrieved_user and retrieved_user.is_principal_investigator:
            print("✓ Principal investigator role works correctly")
        else:
            print("✗ Principal investigator role failed")
            
        db.session.delete(retrieved_user)
        db.session.commit()

def test_admin_patient_restriction():
    """Test that admin access restrictions are in place"""
    print("Testing admin patient access restrictions...")
    
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        
        # Import here to avoid circular imports
        from app.views.main import main_bp
        from flask_login import login_user
        
        # Create admin user
        admin_user = User(username='testadmin', is_admin=True)
        admin_user.set_password('testpass')
        db.session.add(admin_user)
        db.session.commit()
        
        # Test client
        with app.test_client() as client:
            # Login as admin
            response = client.post('/auth/login', data={
                'username': 'testadmin',
                'password': 'testpass',
                'auth_method': 'local'
            }, follow_redirects=True)
            
            # Try to access patient creation (should be redirected)
            response = client.get('/')
            if 'administrators cannot create' in response.get_data(as_text=True).lower() or response.status_code == 302:
                print("✓ Admin patient creation restriction works")
            else:
                print("✗ Admin patient creation restriction failed")
        
        db.session.delete(admin_user)
        db.session.commit()

def test_security_fix():
    """Test that unauthorized user error message doesn't leak authorized users"""
    print("Testing security fix for unauthorized user message...")
    
    app = create_app('testing')
    with app.app_context():
        with app.test_client() as client:
            # Try to login with non-existent user
            response = client.post('/auth/login', data={
                'username': 'nonexistentuser',
                'password': 'wrongpass',
                'auth_method': 'local'
            })
            
            response_text = response.get_data(as_text=True)
            if 'authorized users:' not in response_text.lower() and 'access denied' in response_text.lower():
                print("✓ Security fix works - no user list leaked")
            else:
                print("✗ Security fix failed - authorized users may be exposed")

def main():
    """Run all specification tests"""
    print("CARPEM Oncocentre - Specification Updates Test")
    print("=" * 46)
    
    try:
        test_principal_investigator_role()
        test_admin_patient_restriction()
        test_security_fix()
        
        print("\n✓ All specification updates have been tested!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())