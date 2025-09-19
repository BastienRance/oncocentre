#!/usr/bin/env python3
"""
User Management Script for CARPEM Oncocentre
Creates and manages authorized users for the application.
"""

import sys
import getpass
from app import create_app
from models import db, User

def create_user(username, password=None):
    """Create a new user"""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists!")
            return False
        
        # Get password if not provided
        if password is None:
            password = getpass.getpass(f"Enter password for user '{username}': ")
            password_confirm = getpass.getpass("Confirm password: ")
            
            if password != password_confirm:
                print("❌ Passwords do not match!")
                return False
        
        # Validate password strength
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long!")
            return False
        
        # Create user
        user = User(username=username)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ User '{username}' created successfully!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating user: {e}")
            return False

def list_users():
    """List all users"""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("📋 No users found.")
            return
        
        print("📋 Registered Users:")
        print("-" * 40)
        for user in users:
            status = "🟢 Active" if user.is_active else "🔴 Inactive"
            print(f"👤 {user.username:<20} {status}")
            print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Patients: {len(user.patients)}")
            print()

def deactivate_user(username):
    """Deactivate a user"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found!")
            return False
        
        user.is_active = False
        try:
            db.session.commit()
            print(f"✅ User '{username}' deactivated successfully!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deactivating user: {e}")
            return False

def activate_user(username):
    """Activate a user"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found!")
            return False
        
        user.is_active = True
        try:
            db.session.commit()
            print(f"✅ User '{username}' activated successfully!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error activating user: {e}")
            return False

def reset_password(username):
    """Reset user password"""
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found!")
            return False
        
        new_password = getpass.getpass(f"Enter new password for '{username}': ")
        password_confirm = getpass.getpass("Confirm new password: ")
        
        if new_password != password_confirm:
            print("❌ Passwords do not match!")
            return False
        
        if len(new_password) < 8:
            print("❌ Password must be at least 8 characters long!")
            return False
        
        user.set_password(new_password)
        try:
            db.session.commit()
            print(f"✅ Password reset for user '{username}' successfully!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting password: {e}")
            return False

def setup_initial_users():
    """Setup initial users for the application"""
    print("🔐 CARPEM Oncocentre - Initial User Setup")
    print("=" * 45)
    
    # Create admin user
    print("\n👑 Creating administrator account...")
    admin_created = create_user('admin')
    
    if admin_created:
        print("\n📋 Add more users? (y/n): ", end="")
        while input().lower() == 'y':
            print("\nEnter username: ", end="")
            username = input().strip()
            if username:
                create_user(username)
            print("\nAdd another user? (y/n): ", end="")
    
    print(f"\n✅ Initial setup complete!")
    print(f"📍 Remember to add usernames to AUTHORIZED_USERS environment variable")
    print(f"📍 Current users should be added to: admin,{','.join(['user1', 'user2'])}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🔐 CARPEM Oncocentre User Management")
        print("=" * 40)
        print("Usage:")
        print("  python manage_users.py setup           - Setup initial users")
        print("  python manage_users.py create <user>   - Create new user")
        print("  python manage_users.py list            - List all users")
        print("  python manage_users.py activate <user> - Activate user")
        print("  python manage_users.py deactivate <user> - Deactivate user")
        print("  python manage_users.py reset <user>    - Reset user password")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        setup_initial_users()
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Please provide username: python manage_users.py create <username>")
            return
        create_user(sys.argv[2])
    elif command == 'list':
        list_users()
    elif command == 'activate':
        if len(sys.argv) < 3:
            print("❌ Please provide username: python manage_users.py activate <username>")
            return
        activate_user(sys.argv[2])
    elif command == 'deactivate':
        if len(sys.argv) < 3:
            print("❌ Please provide username: python manage_users.py deactivate <username>")
            return
        deactivate_user(sys.argv[2])
    elif command == 'reset':
        if len(sys.argv) < 3:
            print("❌ Please provide username: python manage_users.py reset <username>")
            return
        reset_password(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()