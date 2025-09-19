#!/usr/bin/env python3
"""
Debug login issues for CARPEM Oncocentre
"""

import os
from app import create_app
from models import db, User

def debug_authorization():
    """Debug authorization setup"""
    print("=== Authorization Debug ===")
    
    # Check environment variable
    env_users = os.environ.get('AUTHORIZED_USERS', '')
    print(f"Environment AUTHORIZED_USERS: '{env_users}'")
    
    # Check what auth.py sees
    import auth
    print(f"auth.AUTHORIZED_USERS set: {auth.AUTHORIZED_USERS}")
    
    # Test with specific user
    test_username = 'admin'
    is_authorized = test_username in auth.AUTHORIZED_USERS
    print(f"Is '{test_username}' authorized: {is_authorized}")
    
    return env_users, auth.AUTHORIZED_USERS

def debug_user_database():
    """Debug user database"""
    print("\n=== User Database Debug ===")
    
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        
        for user in users:
            print(f"- Username: {user.username}")
            print(f"  Active: {user.is_active}")
            print(f"  Password check (admin123): {user.check_password('admin123') if user.username == 'admin' else 'N/A'}")
            print(f"  Created: {user.created_at}")

def test_login_process():
    """Test the complete login process"""
    print("\n=== Login Process Test ===")
    
    # Set environment variable explicitly
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    # Reload auth module to pick up new environment
    import importlib
    import auth
    importlib.reload(auth)
    
    print(f"Updated AUTHORIZED_USERS: {auth.AUTHORIZED_USERS}")
    
    app = create_app()
    
    with app.app_context():
        # Test user lookup
        user = User.query.filter_by(username='admin').first()
        if user:
            print(f"User 'admin' found in database: YES")
            print(f"User active: {user.is_active}")
            print(f"Password check: {user.check_password('admin123')}")
            
            # Check authorization
            is_authorized = 'admin' in auth.AUTHORIZED_USERS
            print(f"User 'admin' in whitelist: {is_authorized}")
            
            if is_authorized and user.check_password('admin123') and user.is_active:
                print("LOGIN SHOULD WORK: All conditions met")
            else:
                print("LOGIN WILL FAIL: Missing conditions")
                if not is_authorized:
                    print("  - User not in whitelist")
                if not user.check_password('admin123'):
                    print("  - Password incorrect")
                if not user.is_active:
                    print("  - User not active")
        else:
            print("User 'admin' found in database: NO")

def fix_authorization():
    """Fix authorization by updating auth.py"""
    print("\n=== Fixing Authorization ===")
    
    # Set environment variable
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    # Update auth.py to reload the environment variable
    import auth
    auth.AUTHORIZED_USERS = set(os.environ.get('AUTHORIZED_USERS', 'admin,user1,user2').split(','))
    
    print(f"Fixed AUTHORIZED_USERS: {auth.AUTHORIZED_USERS}")
    print("Authorization should now work!")

def main():
    """Run all debug functions"""
    print("CARPEM Oncocentre - Login Debug Tool")
    print("=" * 40)
    
    debug_authorization()
    debug_user_database()
    test_login_process()
    fix_authorization()
    
    print("\n" + "=" * 40)
    print("Debug complete!")
    print("\nTo ensure login works:")
    print("1. Make sure AUTHORIZED_USERS environment variable is set")
    print("2. Restart the application after setting the variable")
    print("3. Use these credentials:")
    print("   - admin / admin123")
    print("   - user1 / user1123")
    print("   - etc.")

if __name__ == '__main__':
    main()