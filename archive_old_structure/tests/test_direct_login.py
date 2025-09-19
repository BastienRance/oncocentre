#!/usr/bin/env python3
"""
Test login bypassing SQLAlchemy caching issues
"""

import os
import sqlite3
import bcrypt
from flask import Flask, request, jsonify, render_template_string

def create_test_app():
    """Create a minimal test app"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Set environment
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    @app.route('/')
    def home():
        return '''
        <html>
        <body>
        <h2>Admin Login Test</h2>
        <form method="POST" action="/test_login">
            Username: <input type="text" name="username" value="admin"><br><br>
            Password: <input type="password" name="password" value="admin123"><br><br>
            <input type="submit" value="Test Login">
        </form>
        </body>
        </html>
        '''
    
    @app.route('/test_login', methods=['POST'])
    def test_login():
        """Test login using direct database access"""
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check authorization first
        authorized_users = os.environ.get('AUTHORIZED_USERS', '').split(',')
        if username not in authorized_users:
            return jsonify({
                'success': False,
                'message': f'User {username} not authorized. Authorized: {authorized_users}'
            })
        
        # Direct database check
        try:
            conn = sqlite3.connect('oncocentre.db')
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT username, password_hash, is_admin, is_active FROM user WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return jsonify({
                    'success': False,
                    'message': f'User {username} not found in database'
                })
            
            stored_username, password_hash, is_admin, is_active = result
            
            if not is_active:
                return jsonify({
                    'success': False,
                    'message': f'User {username} is not active'
                })
            
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                return jsonify({
                    'success': True,
                    'username': stored_username,
                    'is_admin': bool(is_admin),
                    'message': 'Login successful! This proves the database is working correctly.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Invalid password'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Database error: {e}'
            })
    
    @app.route('/admin_test')
    def admin_test():
        """Test admin functionality"""
        return jsonify({
            'message': 'Admin area accessible',
            'database_users': get_all_users()
        })
    
    def get_all_users():
        """Get all users from database"""
        try:
            conn = sqlite3.connect('oncocentre.db')
            cursor = conn.cursor()
            cursor.execute("SELECT username, is_admin, is_active FROM user")
            users = cursor.fetchall()
            conn.close()
            return [{'username': u[0], 'is_admin': bool(u[1]), 'is_active': bool(u[2])} for u in users]
        except Exception as e:
            return [{'error': str(e)}]
    
    return app

def main():
    """Main test function"""
    print("CARPEM Oncocentre - Direct Login Test")
    print("=" * 40)
    
    app = create_test_app()
    
    print("Starting test server...")
    print("Go to: http://localhost:5001")
    print("Test the admin login there")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(debug=True, port=5001, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\nTest server stopped")

if __name__ == '__main__':
    main()