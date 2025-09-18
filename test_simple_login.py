#!/usr/bin/env python3
"""
Simple login test to isolate the issue
"""

import os
from app import create_app
from models import db, User

def test_simple_login():
    """Test login with minimal setup"""
    # Set environment
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            # Verify user exists
            user = User.query.filter_by(username='admin').first()
            print(f"User 'admin' exists: {user is not None}")
            if user:
                print(f"User active: {user.is_active}")
                print(f"Password correct: {user.check_password('admin123')}")
            
            # Test login page
            response = client.get('/auth/login')
            print(f"Login page status: {response.status_code}")
            
            # Test login POST
            response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            print(f"Login POST status: {response.status_code}")
            
            if response.status_code == 302:  # Redirect
                print("Login successful - redirecting")
                location = response.headers.get('Location', 'No location header')
                print(f"Redirect to: {location}")
                return True
            else:
                print("Login failed - no redirect")
                response_text = response.data.decode('utf-8', errors='ignore')
                
                # Look for error messages
                if 'alert' in response_text:
                    import re
                    alerts = re.findall(r'alert[^>]*>([^<]+)', response_text)
                    for alert in alerts:
                        print(f"Alert: {alert.strip()}")
                
                # Check form validation
                if 'This field is required' in response_text:
                    print("Form validation error: required fields missing")
                
                return False

if __name__ == '__main__':
    print("Simple Login Test")
    print("=" * 20)
    success = test_simple_login()
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")