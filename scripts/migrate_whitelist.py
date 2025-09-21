#!/usr/bin/env python3
"""
Database migration script to add WhitelistEntry table and migrate existing users
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.core.models import db, WhitelistEntry, User

def migrate_whitelist():
    """Create WhitelistEntry table and migrate environment users"""
    app = create_app()

    with app.app_context():
        # Create the tables
        db.create_all()
        print("OK Database tables created/updated")

        # Find admin user to use as creator
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("WARN No admin user found. Creating default admin user...")
            admin_user = User(username='admin', is_admin=True, is_active=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("OK Admin user created")

        # Migrate environment whitelist to database
        added_count = WhitelistEntry.migrate_from_env(admin_user.id)
        print(f"OK Migrated {added_count} usernames from environment to database")

        # Show current whitelist status
        env_users = set(os.environ.get('AUTHORIZED_USERS', 'admin,user1,user2,doctor1,researcher1').split(','))
        db_users = WhitelistEntry.get_authorized_usernames()

        print(f"\nCurrent whitelist status:")
        print(f"   Environment users: {len(env_users)} ({', '.join(sorted(env_users))})")
        print(f"   Database users: {len(db_users)} ({', '.join(sorted(db_users))})")

        if db_users:
            print(f"\nOK Database whitelist is active and will be used for authentication")
        else:
            print(f"\nWARN Database whitelist is empty, falling back to environment variable")

if __name__ == '__main__':
    migrate_whitelist()