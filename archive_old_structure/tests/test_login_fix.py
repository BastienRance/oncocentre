#!/usr/bin/env python3
"""
Test login functionality after fixes
"""

import os
from app import create_app
from models import db, User

def test_login_functionality():
    """Test that login now works correctly"""
    print("Testing Login Functionality")
    print("=" * 30)
    
    # Set environment variable
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    app = create_app()
    
    with app.app_context():
        # Check users exist
        print("\n1. Checking users in database:")
        users = User.query.all()
        for user in users:
            print(f"   - {user.username} (active: {user.is_active})")
        
        # Test authorization system
        print("\n2. Testing authorization system:")
        import auth
        importlib.reload(auth)  # Reload to pick up environment variable
        
        print(f"   Authorized users: {sorted(auth.get_authorized_users())}")
        
        # Test specific user
        test_user = User.query.filter_by(username='admin').first()
        if test_user:
            print(f"\n3. Testing user 'admin':")
            print(f"   - Found in database: YES")
            print(f"   - Is active: {test_user.is_active}")
            print(f"   - Password check (admin123): {test_user.check_password('admin123')}")
            print(f"   - In authorized list: {'admin' in auth.get_authorized_users()}")
            
            # All conditions for successful login
            can_login = (
                test_user.is_active and 
                test_user.check_password('admin123') and 
                'admin' in auth.get_authorized_users()
            )
            print(f"   - CAN LOGIN: {can_login}")
        else:
            print(f"\n3. Testing user 'admin': NOT FOUND")
            return False
    
    # Test with Flask test client
    print("\n4. Testing with web client:")
    
    client = app.test_client()
    
    # Test login page loads
    response = client.get('/auth/login')
    if response.status_code == 200:
        print("   - Login page loads: OK")
    else:
        print(f"   - Login page loads: FAILED (status {response.status_code})")
        return False
    
    # Test actual login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': ''  # Disabled for testing
    }, follow_redirects=True)
    
    # Check for success indicators
    response_text = response.data.decode('utf-8', errors='ignore')
    
    if 'Connexion réussie' in response_text or 'Bienvenue' in response_text:
        print("   - Login attempt: SUCCESS")
        return True
    elif 'CARPEM Oncocentre' in response_text and 'Créer Identifiant' in response_text:
        print("   - Login attempt: SUCCESS (redirected to main page)")
        return True
    elif 'non autorisé' in response_text:
        print("   - Login attempt: FAILED - Authorization issue")
        print("     Check AUTHORIZED_USERS environment variable")
        return False
    elif 'incorrect' in response_text:
        print("   - Login attempt: FAILED - Wrong password")
        return False
    elif 'non trouvé' in response_text:
        print("   - Login attempt: FAILED - User not found")
        return False
    elif 'Connexion' in response_text and 'login' in response_text.lower():
        print("   - Login attempt: FAILED - Still on login page")
        # Look for error messages
        if 'alert' in response_text:
            import re
            alerts = re.findall(r'<div class="alert[^>]*>(.*?)</div>', response_text, re.DOTALL)
            for alert in alerts:
                clean_alert = re.sub(r'<[^>]+>', '', alert).strip()
                if clean_alert:
                    print(f"     Error message: {clean_alert}")
        return False
    else:
        print("   - Login attempt: UNKNOWN RESULT")
        print(f"     Response length: {len(response_text)} chars")
        print(f"     Contains 'login': {'login' in response_text.lower()}")
        print(f"     Contains 'Connexion': {'Connexion' in response_text}")
        print(f"     Response start: {response_text[:300]}")
        return False

def main():
    """Main test function"""
    print("CARPEM Oncocentre - Login Fix Test")
    print("=" * 40)
    
    # Import after setting environment
    import importlib
    
    if test_login_functionality():
        print(f"\nSUCCESS: LOGIN FUNCTIONALITY WORKING!")
        print(f"\nReady to use:")
        print(f"1. Start the server: python run_https.py")
        print(f"2. Go to: https://localhost:5000")
        print(f"3. Login with: admin / admin123")
        return True
    else:
        print(f"\nFAILED: LOGIN STILL NOT WORKING")
        print(f"Check the error messages above for specific issues")
        return False

if __name__ == '__main__':
    import importlib
    success = main()
    exit(0 if success else 1)