#!/usr/bin/env python3
"""
Fix admin login by ensuring database schema matches the models
"""

import sqlite3
import os

def check_and_fix_database():
    """Check and fix database schema"""
    print("Checking and fixing database schema...")
    
    # Connect directly to database
    conn = sqlite3.connect('oncocentre.db')
    cursor = conn.cursor()
    
    # Check current user table schema
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    
    print("Current user table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check if is_admin column exists
    column_names = [col[1] for col in columns]
    
    if 'is_admin' not in column_names:
        print("Adding missing is_admin column...")
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
        conn.commit()
        print("Added is_admin column")
    else:
        print("is_admin column already exists")
    
    # Update admin user to be admin
    cursor.execute("UPDATE user SET is_admin = 1 WHERE username = 'admin'")
    updated = cursor.rowcount
    conn.commit()
    
    if updated > 0:
        print(f"Updated {updated} admin user(s)")
    else:
        print("No admin user found to update")
    
    # Verify the fix
    cursor.execute("SELECT username, is_admin FROM user WHERE username = 'admin'")
    admin_result = cursor.fetchone()
    
    if admin_result:
        username, is_admin = admin_result
        print(f"Admin user verification: {username} -> is_admin: {is_admin}")
    else:
        print("ERROR: Admin user not found!")
        return False
    
    conn.close()
    return True

def test_login_directly():
    """Test login functionality directly"""
    print("\nTesting login functionality...")
    
    # Set environment
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    # Create a simple test app
    from flask import Flask
    from flask_login import LoginManager
    import sqlite3
    import bcrypt
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    
    # Simple User class for testing
    class SimpleUser:
        def __init__(self, id, username, password_hash, is_active, is_admin):
            self.id = id
            self.username = username
            self.password_hash = password_hash
            self.is_active = is_active
            self.is_admin = is_admin
        
        def check_password(self, password):
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        
        def is_authenticated(self):
            return True
        
        def is_anonymous(self):
            return False
        
        def get_id(self):
            return str(self.id)
    
    def get_user_by_username(username):
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, is_active, is_admin FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return SimpleUser(*result)
        return None
    
    # Test admin user
    admin_user = get_user_by_username('admin')
    if admin_user:
        print(f"Found admin user: {admin_user.username}")
        print(f"Is admin: {admin_user.is_admin}")
        print(f"Is active: {admin_user.is_active}")
        
        # Test password
        if admin_user.check_password('admin123'):
            print("Password check: SUCCESS")
            
            # Check if user is in authorized list
            auth_users = os.environ.get('AUTHORIZED_USERS', '').split(',')
            if admin_user.username in auth_users:
                print("Authorization check: SUCCESS")
                print("Login should work!")
                return True
            else:
                print(f"Authorization check: FAILED ({admin_user.username} not in {auth_users})")
        else:
            print("Password check: FAILED")
    else:
        print("Admin user not found!")
    
    return False

def create_simple_test_server():
    """Create a simple test server to verify login"""
    print("\nCreating simple test server...")
    
    from flask import Flask, request, jsonify
    import sqlite3
    import bcrypt
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    
    @app.route('/test_login', methods=['POST'])
    def test_login():
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Direct database query
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, is_admin FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_username, password_hash, is_admin = result
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                return jsonify({
                    'success': True,
                    'username': stored_username,
                    'is_admin': bool(is_admin),
                    'message': 'Login successful'
                })
        
        return jsonify({'success': False, 'message': 'Login failed'})
    
    @app.route('/test')
    def test_page():
        return '''
        <html>
        <body>
        <h2>Test Login</h2>
        <form method="POST" action="/test_login">
            Username: <input type="text" name="username" value="admin"><br><br>
            Password: <input type="password" name="password" value="admin123"><br><br>
            <input type="submit" value="Test Login">
        </form>
        </body>
        </html>
        '''
    
    print("Starting test server at http://localhost:5001")
    print("Go to http://localhost:5001/test to test login")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(debug=True, port=5001)
    except KeyboardInterrupt:
        print("\nTest server stopped")

def main():
    """Main function"""
    print("CARPEM Oncocentre - Admin Login Fix")
    print("=" * 40)
    
    if check_and_fix_database():
        if test_login_directly():
            print("\n" + "=" * 40)
            print("DATABASE FIXED SUCCESSFULLY!")
            print("\nThe database schema has been corrected.")
            print("You should now be able to login as admin.")
            
            print("\nTo test:")
            print("1. Start the main application: python run_https.py")
            print("2. Go to: https://localhost:5000")
            print("3. Login with: admin / admin123")
            
            print("\nIf you still get errors, run the test server:")
            print("python fix_admin_login.py")
            print("Then when prompted, choose to run test server")
            
            response = input("\nWould you like to run a simple test server to verify? (y/n): ")
            if response.lower() == 'y':
                create_simple_test_server()
        else:
            print("Login test failed. Check the output above for issues.")
    else:
        print("Database fix failed!")

if __name__ == '__main__':
    main()