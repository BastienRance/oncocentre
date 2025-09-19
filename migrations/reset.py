#!/usr/bin/env python3
"""
Database reset utility
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import db, User

def reset_database():
    """Reset the entire database and create initial admin user"""
    print("Resetting Database with Admin Support")
    print("=" * 40)
    
    # Remove existing database files
    db_files = ['oncocentre.db', 'instance/oncocentre.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Removed existing database: {db_file}")
    
    # Create fresh database
    app = create_app('development')
    
    with app.app_context():
        try:
            print("Creating new database...")
            db.create_all()
            
            # Create admin user
            admin_user = User(username='admin', is_admin=True)
            admin_user.set_password('admin123')
            
            # Create test users
            users_data = [
                ('user1', 'user1123', False),
                ('user2', 'user2123', False),
                ('doctor1', 'doctor123', False),
                ('researcher1', 'research123', False)
            ]
            
            db.session.add(admin_user)
            
            for username, password, is_admin in users_data:
                user = User(username=username, is_admin=is_admin)
                user.set_password(password)
                db.session.add(user)
            
            db.session.commit()
            print("✅ Database reset and users created successfully!")
            
        except Exception as e:
            print(f"ERROR: Failed to create users: {e}")
            return False
    
    print("\nDatabase reset complete!")
    print("You can now test admin functionality:")
    print("1. Start the server: python run.py")
    print("2. Login as: admin / admin123")
    print("3. Access admin features from the navigation menu")
    return True

if __name__ == "__main__":
    response = input("This will reset the entire database!\nAre you sure? (yes/no): ")
    if response.lower() == 'yes':
        success = reset_database()
        sys.exit(0 if success else 1)
    else:
        print("Database reset cancelled.")
        sys.exit(0)