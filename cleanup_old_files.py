#!/usr/bin/env python3
"""
Clean up old files after refactoring
"""

import os
import shutil

# Files to move to archive
old_files = [
    'admin.py', 'auth.py', 'routes.py', 'forms.py', 'models.py', 'utils.py',
    'app.py', 'create_test_users.py', 'make_admin.py', 'manage_users.py',
    'migrate_database.py', 'reset_database.py', 'run_https.py',
    'check_database.py'
]

# Test files to move to archive
test_files = [
    'test_admin_functionality.py', 'test_direct_login.py', 'test_functionality.py',
    'test_login_fix.py', 'test_patient_creation_user1.py', 'test_security_fixed.py',
    'test_security.py', 'test_simple_login.py', 'test_direct_patient_creation.py'
]

# Scripts to move to archive
script_files = [
    'ADMIN_SETUP_COMPLETE.py', 'complete_admin_solution.py', 'debug_admin_login.py',
    'debug_login.py', 'final_admin_fix.py', 'FINAL_LOGIN_TEST.py', 'fix_admin_login.py',
    'setup_complete_system.py', 'simple_setup.py', 'working_migration.py'
]

def cleanup_files():
    """Move old files to archive directory"""
    
    # Create archive directory
    archive_dir = 'archive_old_structure'
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        os.makedirs(os.path.join(archive_dir, 'tests'))
        os.makedirs(os.path.join(archive_dir, 'scripts'))
    
    moved_files = []
    
    # Move old core files
    for filename in old_files:
        if os.path.exists(filename):
            shutil.move(filename, archive_dir)
            moved_files.append(filename)
            print(f"Moved {filename} to {archive_dir}/")
    
    # Move old test files
    for filename in test_files:
        if os.path.exists(filename):
            shutil.move(filename, os.path.join(archive_dir, 'tests'))
            moved_files.append(filename)
            print(f"Moved {filename} to {archive_dir}/tests/")
    
    # Move old script files
    for filename in script_files:
        if os.path.exists(filename):
            shutil.move(filename, os.path.join(archive_dir, 'scripts'))
            moved_files.append(filename)
            print(f"Moved {filename} to {archive_dir}/scripts/")
    
    print(f"\nMoved {len(moved_files)} files to archive")
    print(f"Archived files can be found in: {archive_dir}/")
    
    # List remaining files at root
    remaining = [f for f in os.listdir('.') if f.endswith('.py') and os.path.isfile(f)]
    remaining = [f for f in remaining if f not in ['run.py', 'cleanup_old_files.py']]
    
    if remaining:
        print(f"\nRemaining Python files at root level:")
        for f in remaining:
            print(f"  - {f}")
    else:
        print(f"\n✅ Root level cleaned up successfully!")

if __name__ == "__main__":
    cleanup_files()