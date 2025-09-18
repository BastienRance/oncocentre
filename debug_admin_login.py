#!/usr/bin/env python3
"""
Debug admin login issues for CARPEM Oncocentre
"""

import os
import traceback

def debug_admin_login():
    """Debug the admin login process step by step"""
    print("Debugging Admin Login Issue")
    print("=" * 30)
    
    try:
        # Set environment
        os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
        
        # Import application
        print("1. Importing application...")
        from app import create_app
        from models import db, User
        
        app = create_app()
        app.config['DEBUG'] = True  # Enable debug mode
        
        print("2. Testing database connection...")
        with app.app_context():
            # Test database query
            try:
                user_count = User.query.count()
                print(f"   Database connection: OK ({user_count} users)")
            except Exception as e:
                print(f"   Database error: {e}")
                return False
            
            # Test admin user
            try:
                admin_user = User.query.filter_by(username='admin').first()
                if admin_user:
                    print(f"   Admin user found: {admin_user.username}")
                    print(f"   Is admin: {admin_user.is_admin}")
                    print(f"   Is active: {admin_user.is_active}")
                else:
                    print("   ERROR: Admin user not found!")
                    return False
            except Exception as e:
                print(f"   Admin user query error: {e}")
                return False
        
        print("3. Testing login route...")
        with app.test_client() as client:
            try:
                # Test GET login page
                response = client.get('/auth/login')
                print(f"   Login page GET: {response.status_code}")
                if response.status_code != 200:
                    print(f"   Login page error: {response.data}")
                
                # Test POST login
                print("4. Testing admin login POST...")
                response = client.post('/auth/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                }, follow_redirects=False)
                
                print(f"   Login POST status: {response.status_code}")
                
                if response.status_code == 302:
                    print("   Login successful - redirecting")
                    location = response.headers.get('Location', 'No location')
                    print(f"   Redirect to: {location}")
                    
                    # Test accessing redirect location
                    if location:
                        response = client.get(location)
                        print(f"   Redirect page status: {response.status_code}")
                        if response.status_code != 200:
                            print(f"   Redirect page error")
                            print(f"   Response data: {response.data[:500]}")
                
                elif response.status_code == 500:
                    print("   Internal Server Error during login")
                    print(f"   Response: {response.data}")
                else:
                    print(f"   Login failed with status: {response.status_code}")
                    print(f"   Response: {response.data}")
                
            except Exception as e:
                print(f"   Login test error: {e}")
                traceback.print_exc()
                return False
        
        print("5. Testing admin dashboard directly...")
        with app.test_client() as client:
            try:
                # Login first
                client.post('/auth/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                })
                
                # Test admin dashboard
                response = client.get('/admin/dashboard')
                print(f"   Admin dashboard status: {response.status_code}")
                
                if response.status_code == 500:
                    print("   ERROR: Admin dashboard internal error")
                    print(f"   Response: {response.data[:500]}")
                elif response.status_code == 403:
                    print("   ERROR: Admin access forbidden")
                elif response.status_code == 200:
                    print("   Admin dashboard: OK")
                
            except Exception as e:
                print(f"   Admin dashboard error: {e}")
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Debug failed: {e}")
        traceback.print_exc()
        return False

def test_template_rendering():
    """Test if templates are rendering correctly"""
    print("\n6. Testing template rendering...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test rendering login template
            from flask import render_template
            from forms import LoginForm
            
            form = LoginForm()
            html = render_template('login.html', form=form)
            print("   Login template: OK")
            
            # Test rendering admin dashboard
            stats = {
                'total_users': 5,
                'active_users': 5,
                'admin_users': 1,
                'total_patients': 0,
                'recent_users': []
            }
            
            html = render_template('admin/dashboard.html', stats=stats)
            print("   Admin dashboard template: OK")
            
    except Exception as e:
        print(f"   Template rendering error: {e}")
        traceback.print_exc()

def run_debug_server():
    """Run server with debug output"""
    print("\n7. Starting debug server...")
    print("   Watch for error messages in the output")
    print("   Press Ctrl+C to stop")
    
    try:
        os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
        from app import create_app
        
        app = create_app()
        app.config['DEBUG'] = True
        
        print("   Starting server at http://localhost:5000")
        print("   Try logging in and watch for error messages")
        
        app.run(debug=True, port=5000)
        
    except KeyboardInterrupt:
        print("\n   Debug server stopped")
    except Exception as e:
        print(f"   Server error: {e}")
        traceback.print_exc()

def main():
    """Main debug function"""
    if debug_admin_login():
        test_template_rendering()
        
        print("\n" + "=" * 30)
        print("Debug completed. If no obvious errors were found,")
        print("run the debug server to see live error messages:")
        print("\nWould you like to start the debug server? (y/n): ", end="")
        
        try:
            response = input()
            if response.lower() == 'y':
                run_debug_server()
        except:
            pass

if __name__ == '__main__':
    main()