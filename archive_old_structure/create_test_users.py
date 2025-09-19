#!/usr/bin/env python3
"""
Create test users for CARPEM Oncocentre
"""

from app import create_app
from models import db, User

def create_test_users():
    """Create test users with predefined passwords"""
    app = create_app()
    
    with app.app_context():
        # Create test users
        test_users = [
            ('admin', 'admin123'),
            ('user1', 'user1123'),
            ('user2', 'user2123'),
            ('doctor1', 'doctor123'),
            ('researcher1', 'research123')
        ]
        
        created_users = []
        
        for username, password in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"WARNING: User '{username}' already exists!")
                continue
            
            # Create user
            user = User(username=username)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                created_users.append(username)
                print(f"SUCCESS: User '{username}' created successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"ERROR: Error creating user '{username}': {e}")
        
        if created_users:
            print(f"\nSuccessfully created {len(created_users)} users:")
            for username in created_users:
                print(f"   - {username}")
            
            print(f"\nAdd these users to AUTHORIZED_USERS environment variable:")
            print(f"   export AUTHORIZED_USERS=\"{','.join(['admin', 'user1', 'user2', 'doctor1', 'researcher1'])}\"")
            
            print(f"\nTest Credentials:")
            print(f"   admin / admin123")
            print(f"   user1 / user1123")
            print(f"   user2 / user2123")
            print(f"   doctor1 / doctor123")
            print(f"   researcher1 / research123")
        else:
            print("INFO: No new users were created.")

if __name__ == '__main__':
    print("Creating test users for CARPEM Oncocentre...")
    create_test_users()