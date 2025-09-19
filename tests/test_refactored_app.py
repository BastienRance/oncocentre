#!/usr/bin/env python3
"""
Comprehensive test of the refactored CARPEM Oncocentre application
"""

import requests
import sys
import os
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
ADMIN_CREDENTIALS = ("admin", "admin123")
USER_CREDENTIALS = ("user1", "user1123")

def test_basic_endpoints():
    """Test basic endpoint accessibility"""
    print("🧪 Testing Basic Endpoints")
    print("=" * 30)
    
    session = requests.Session()
    
    # Test login page
    response = session.get(f"{BASE_URL}/auth/login")
    if response.status_code == 200:
        print("✅ Login page accessible")
    else:
        print(f"❌ Login page failed: {response.status_code}")
        return False
    
    # Test unauthorized access to main page
    response = session.get(f"{BASE_URL}/")
    # Flask-Login redirects to login page, which returns 200
    if response.status_code == 200 and 'login' in response.url.lower():
        print("✅ Unauthorized access properly redirected to login")
    elif response.status_code == 302:
        print("✅ Unauthorized access properly redirected")
    else:
        print(f"❌ Unauthorized access not handled: {response.status_code}")
        return False
    
    return True

def login_user(session, username, password):
    """Helper function to login a user"""
    try:
        # Get login page for CSRF token
        login_page = session.get(f"{BASE_URL}/auth/login")
        
        # Extract CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("❌ Could not find CSRF token")
            return False
        
        # Submit login
        login_data = {
            'username': username,
            'password': password,
            'csrf_token': csrf_token.get('value')
        }
        
        response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print(f"✅ Login successful for {username}")
            return True
        else:
            print(f"❌ Login failed for {username}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login error for {username}: {e}")
        return False

def test_user_authentication():
    """Test user authentication system"""
    print("\n🧪 Testing User Authentication")
    print("=" * 35)
    
    session = requests.Session()
    
    # Test admin login
    if not login_user(session, *ADMIN_CREDENTIALS):
        return False
    
    # Test access to main page after login
    response = session.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Main page accessible after login")
    else:
        print(f"❌ Main page not accessible after login: {response.status_code}")
        return False
    
    # Test logout
    response = session.get(f"{BASE_URL}/auth/logout")
    if response.status_code == 302:  # Should redirect to login
        print("✅ Logout successful")
    elif response.status_code == 200 and 'login' in response.url.lower():
        print("✅ Logout successful - redirected to login")
    else:
        print(f"❌ Logout failed: {response.status_code}")
        return False
    
    return True

def test_patient_creation():
    """Test patient creation functionality"""
    print("\n🧪 Testing Patient Creation")
    print("=" * 30)
    
    session = requests.Session()
    
    # Login as regular user
    if not login_user(session, *USER_CREDENTIALS):
        return False
    
    # Test ID preview
    try:
        response = session.post(f"{BASE_URL}/preview_id", json={})
        if response.status_code == 200:
            data = response.json()
            next_id = data.get('oncocentre_id')
            print(f"✅ ID preview working: {next_id}")
        else:
            print(f"❌ ID preview failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ID preview error: {e}")
        return False
    
    # Get patient creation form
    main_page = session.get(f"{BASE_URL}/")
    
    # Extract CSRF token for patient form
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(main_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    
    if not csrf_token:
        print("❌ Could not find CSRF token for patient form")
        return False
    
    # Create test patient
    patient_data = {
        'ipp': 'REFACTOR_TEST_001',
        'first_name': 'Test',
        'last_name': 'Patient',
        'birth_date': '1990-01-01',
        'sex': 'M',
        'csrf_token': csrf_token.get('value')
    }
    
    response = session.post(f"{BASE_URL}/create_patient", data=patient_data, allow_redirects=False)
    
    if response.status_code == 302:
        print("✅ Patient creation successful")
    else:
        print(f"❌ Patient creation failed: {response.status_code}")
        return False
    
    # Test patient list
    response = session.get(f"{BASE_URL}/patients")
    if response.status_code == 200:
        print("✅ Patient list accessible")
        
        # Check if patient appears in list
        if 'REFACTOR_TEST_001' in response.text:
            print("✅ Created patient appears in list")
        else:
            print("⚠️  Created patient not found in list (may be encrypted)")
        
    else:
        print(f"❌ Patient list failed: {response.status_code}")
        return False
    
    return True

def test_admin_functionality():
    """Test admin functionality"""
    print("\n🧪 Testing Admin Functionality")
    print("=" * 32)
    
    session = requests.Session()
    
    # Login as admin
    if not login_user(session, *ADMIN_CREDENTIALS):
        return False
    
    # Test admin dashboard
    response = session.get(f"{BASE_URL}/admin/dashboard")
    if response.status_code == 200:
        print("✅ Admin dashboard accessible")
    else:
        print(f"❌ Admin dashboard failed: {response.status_code}")
        return False
    
    # Test user list
    response = session.get(f"{BASE_URL}/admin/users")
    if response.status_code == 200:
        print("✅ User management accessible")
    else:
        print(f"❌ User management failed: {response.status_code}")
        return False
    
    # Test system info
    response = session.get(f"{BASE_URL}/admin/system-info")
    if response.status_code == 200:
        print("✅ System info accessible")
    else:
        print(f"❌ System info failed: {response.status_code}")
        return False
    
    return True

def test_regular_user_admin_access():
    """Test that regular users cannot access admin functions"""
    print("\n🧪 Testing Admin Access Control")
    print("=" * 33)
    
    session = requests.Session()
    
    # Login as regular user
    if not login_user(session, *USER_CREDENTIALS):
        return False
    
    # Try to access admin dashboard
    response = session.get(f"{BASE_URL}/admin/dashboard")
    if response.status_code == 403:
        print("✅ Regular user blocked from admin dashboard")
    else:
        print(f"❌ Regular user accessed admin dashboard: {response.status_code}")
        return False
    
    # Try to access user management
    response = session.get(f"{BASE_URL}/admin/users")
    if response.status_code == 403:
        print("✅ Regular user blocked from user management")
    else:
        print(f"❌ Regular user accessed user management: {response.status_code}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 CARPEM Oncocentre Refactored Application Test Suite")
    print("=" * 55)
    
    # Install beautifulsoup4 if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("📦 Installing beautifulsoup4...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup
    
    tests = [
        ("Basic Endpoints", test_basic_endpoints),
        ("User Authentication", test_user_authentication),
        ("Patient Creation", test_patient_creation),
        ("Admin Functionality", test_admin_functionality),
        ("Admin Access Control", test_regular_user_admin_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored application is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)