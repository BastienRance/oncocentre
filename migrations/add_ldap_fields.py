#!/usr/bin/env python3
"""
Database migration script to add LDAP authentication fields to User table
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate_database():
    """Add LDAP fields to the User table"""
    
    db_path = 'instance/oncocentre.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if LDAP fields already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        ldap_fields = [
            'auth_source',
            'email', 
            'first_name',
            'last_name',
            'display_name',
            'ldap_dn',
            'last_ldap_sync'
        ]
        
        existing_ldap_fields = [field for field in ldap_fields if field in columns]
        
        if existing_ldap_fields:
            print(f"LDAP fields already exist: {existing_ldap_fields}")
            print("Migration may have already been run.")
            
        # Add missing fields
        migrations_applied = 0
        
        if 'auth_source' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN auth_source VARCHAR(20) DEFAULT "local" NOT NULL')
            print("Added auth_source field")
            migrations_applied += 1
            
        if 'email' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN email VARCHAR(120)')
            print("Added email field")
            migrations_applied += 1
            
        if 'first_name' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN first_name VARCHAR(50)')
            print("Added first_name field")
            migrations_applied += 1
            
        if 'last_name' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN last_name VARCHAR(50)')
            print("Added last_name field")
            migrations_applied += 1
            
        if 'display_name' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN display_name VARCHAR(100)')
            print("Added display_name field")
            migrations_applied += 1
            
        if 'ldap_dn' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN ldap_dn TEXT')
            print("Added ldap_dn field")
            migrations_applied += 1
            
        if 'last_ldap_sync' not in columns:
            cursor.execute('ALTER TABLE user ADD COLUMN last_ldap_sync DATETIME')
            print("Added last_ldap_sync field")
            migrations_applied += 1
        
        # Commit changes
        conn.commit()
        
        if migrations_applied > 0:
            print(f"\nMigration completed successfully! Applied {migrations_applied} field additions.")
        else:
            print("No migrations needed - all LDAP fields already exist.")
            
        # Verify the migration
        cursor.execute("PRAGMA table_info(user)")
        columns_after = [row[1] for row in cursor.fetchall()]
        print(f"\nUser table now has {len(columns_after)} columns:")
        for col in sorted(columns_after):
            print(f"  - {col}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("CARPEM Oncocentre - LDAP Fields Migration")
    print("=" * 45)
    print(f"Starting migration at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = migrate_database()
    
    if success:
        print("\n✓ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)