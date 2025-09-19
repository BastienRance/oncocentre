#!/usr/bin/env python3
"""
Grant admin privileges to a user
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import db, User

def make_admin(username):
    """Grant admin privileges to a user"""
    app = create_app('development')
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"ERROR: User '{username}' not found!")
            return False
        
        if user.is_admin:
            print(f"INFO: User '{username}' is already an administrator!")
            return True
        
        user.is_admin = True
        
        try:
            db.session.commit()
            print(f"SUCCESS: User '{username}' is now an administrator!")
            return True
        except Exception as e:
            print(f"ERROR: Failed to update user '{username}': {e}")
            db.session.rollback()
            return False

def list_admins():
    """List all admin users"""
    app = create_app('development')
    
    with app.app_context():
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if admin_users:
            print("Current administrators:")
            for user in admin_users:
                status = "active" if user.is_active else "inactive"
                print(f"  - {user.username} ({status})")
        else:
            print("No administrators found!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python make_admin.py <username>  - Grant admin privileges")
        print("  python make_admin.py list        - List current admins")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_admins()
    else:
        username = command
        success = make_admin(username)
        sys.exit(0 if success else 1)