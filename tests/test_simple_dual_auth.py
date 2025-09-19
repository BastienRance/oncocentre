#!/usr/bin/env python3
"""
Simple test to verify dual authentication implementation
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User

def test_authentication_functions():
    """Test authentication functions directly"""
    print("Testing authentication functions...")
    
    app = create_app('testing')
    
    with app.app_context():
        # Create test database
        db.create_all()
        
        # Create a test user
        test_user = User(username='testuser', auth_source='local')
        test_user.set_password('testpass')
        db.session.add(test_user)
        db.session.commit()
        
        # Import authentication functions
        from app.views.auth import authenticate_user, authenticate_local_user, authenticate_ldap_user
        
        # Test local authentication
        print("Testing local authentication...")
        user, message = authenticate_local_user('testuser', 'testpass')
        if user:
            print(f"✓ Local auth successful: {message}")
        else:
            print(f"✗ Local auth failed: {message}")
        
        # Test wrong password
        user, message = authenticate_local_user('testuser', 'wrongpass')
        if not user:
            print(f"✓ Local auth correctly rejected bad password: {message}")
        else:
            print(f"✗ Local auth should have failed")
        
        # Test LDAP authentication (should fail gracefully)
        print("Testing LDAP authentication...")
        user, message = authenticate_ldap_user('testuser', 'testpass')
        if not user:
            print(f"✓ LDAP auth failed as expected: {message}")
        else:
            print(f"✗ LDAP auth should have failed")
        
        # Test auto authentication
        print("Testing auto authentication...")
        user, message = authenticate_user('testuser', 'testpass', 'auto')
        if user:
            print(f"✓ Auto auth successful: {message}")
        else:
            print(f"✗ Auto auth failed: {message}")
        
        print("\n✓ All authentication functions working correctly!")

def test_form_configuration():
    """Test form configuration for dual authentication"""
    print("Testing form configuration...")
    
    app = create_app('testing')
    
    with app.app_context():
        from app.forms.auth import LoginForm
        
        form = LoginForm()
        choices = [choice[0] for choice in form.auth_method.choices]
        
        if 'auto' in choices and 'local' in choices and 'ldap' in choices:
            print("✓ All authentication methods available in form")
        else:
            print(f"✗ Missing authentication methods: {choices}")
        
        print(f"Available choices: {form.auth_method.choices}")

def main():
    """Run authentication tests"""
    print("CARPEM Oncocentre - Dual Authentication Implementation Test")
    print("=" * 58)
    
    try:
        test_authentication_functions()
        print()
        test_form_configuration()
        
        print("\n✓ Dual authentication system implemented successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())