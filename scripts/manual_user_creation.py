#!/usr/bin/env python3
"""
Manual user creation using direct database access
"""

import sqlite3
import bcrypt
import os

def create_users():
    """Create users directly in the database"""

    # Ensure instance directory exists
    os.makedirs('instance', exist_ok=True)

    # Connect to database
    conn = sqlite3.connect('instance/oncocentre.db')
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(128),
            is_active BOOLEAN DEFAULT 1 NOT NULL,
            is_admin BOOLEAN DEFAULT 0 NOT NULL,
            is_principal_investigator BOOLEAN DEFAULT 0 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            auth_source VARCHAR(20) DEFAULT 'local' NOT NULL,
            email VARCHAR(120),
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            display_name VARCHAR(100),
            ldap_dn TEXT,
            last_ldap_sync DATETIME
        )
    ''')

    users_to_create = [
        ('admin', 'admin123', True, False),  # Admin user
        ('user1', 'user123', False, False),  # Regular user
        ('pi_user', 'pi123', False, True),   # Principal investigator
        ('test_admin', 'test123', True, False),  # Another admin
        ('test_user', 'test123', False, False),   # Another regular user
    ]

    created_count = 0

    for username, password, is_admin, is_pi in users_to_create:
        # Check if user exists
        cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
        if cursor.fetchone():
            print(f"SKIP: User {username} already exists")
            continue

        # Hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Insert user
        cursor.execute('''
            INSERT INTO user (username, password_hash, is_active, is_admin, is_principal_investigator, auth_source)
            VALUES (?, ?, 1, ?, ?, 'local')
        ''', (username, password_hash, is_admin, is_pi))

        created_count += 1
        role = []
        if is_admin:
            role.append("admin")
        if is_pi:
            role.append("PI")
        if not role:
            role.append("user")

        print(f"CREATED: {username} / {password} ({', '.join(role)})")

    # Commit changes
    conn.commit()
    conn.close()

    print(f"\nSuccessfully created {created_count} users")
    print("\nYou can now test with these credentials:")
    print("- admin / admin123 (Admin)")
    print("- user1 / user123 (Regular User)")
    print("- pi_user / pi123 (Principal Investigator)")
    print("- test_admin / test123 (Admin)")
    print("- test_user / test123 (Regular User)")

if __name__ == '__main__':
    create_users()