#!/usr/bin/env python3
"""
Make a user an administrator for CARPEM Oncocentre
"""

import sys
from app import create_app
from models import db, User

def make_admin(username):
    """Make a user an administrator"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"ERROR: User '{username}' not found!")
            return False
        
        if user.is_admin:
            print(f"User '{username}' is already an administrator.")
            return True
        
        user.is_admin = True
        
        try:
            db.session.commit()
            print(f"SUCCESS: User '{username}' is now an administrator!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Could not make user admin: {e}")
            return False

def list_admins():
    """List all administrators"""
    app = create_app()
    
    with app.app_context():
        admins = User.query.filter_by(is_admin=True).all()
        
        if admins:
            print("Current administrators:")
            for admin in admins:
                status = "Active" if admin.is_active else "Inactive"
                print(f"  - {admin.username} ({status})")
        else:
            print("No administrators found.")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Admin Management Tool")
        print("=" * 20)
        print("Usage:")
        print("  python make_admin.py <username>    - Make user an admin")
        print("  python make_admin.py list          - List current admins")
        print("\nExample:")
        print("  python make_admin.py admin")
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        list_admins()
    else:
        username = command
        make_admin(username)

if __name__ == '__main__':
    main()