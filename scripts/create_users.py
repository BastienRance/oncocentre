#!/usr/bin/env python3
"""
Create test users for the CARPEM Oncocentre application
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.core.models import db, User

def create_test_users():
    """Create initial test users"""
    print("Creating test users for CARPEM Oncocentre...")
    
    app = create_app('development')
    
    with app.app_context():
        users_data = [
            ('admin', 'admin123', True),
            ('user1', 'user1123', False),
            ('user2', 'user2123', False),
            ('doctor1', 'doctor123', False),
            ('researcher1', 'research123', False)
        ]
        
        created_users = []
        
        for username, password, is_admin in users_data:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"SKIPPED: User '{username}' already exists!")
                continue
            
            # Create new user
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                print(f"SUCCESS: User '{username}' created successfully!")
                created_users.append(username)
            except Exception as e:
                print(f"ERROR: Failed to create user '{username}': {e}")
                db.session.rollback()
        
        print(f"\nSuccessfully created {len(created_users)} users:")
        for username in created_users:
            print(f"   - {username}")
        
        print(f"\nAdd these users to AUTHORIZED_USERS environment variable:")
        print(f'   export AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"')
        
        print(f"\nTest Credentials:")
        for username, password, is_admin in users_data:
            role = "admin" if is_admin else "user"
            print(f"   {username} / {password} ({role})")

if __name__ == "__main__":
    create_test_users()