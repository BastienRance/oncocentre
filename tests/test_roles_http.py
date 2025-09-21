#!/usr/bin/env python3
"""
HTTP-based role testing for CARPEM Oncocentre
Tests all user roles via HTTP requests with session management
"""

import requests
import sys

class RoleTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def login(self, username, password):
        """Login with credentials"""
        # First get the login page to extract CSRF token
        response = self.session.get(f"{self.base_url}/auth/login")
        if response.status_code != 200:
            print(f"FAIL Cannot access login page for {username}")
            return False

        # Extract CSRF token from the form
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break

        if not csrf_token:
            print(f"FAIL Cannot extract CSRF token for {username}")
            return False

        # Now submit login with CSRF token
        response = self.session.post(f"{self.base_url}/auth/login", data={
            'username': username,
            'password': password,
            'auth_method': 'local',
            'csrf_token': csrf_token
        }, allow_redirects=False)

        if response.status_code == 302:
            print(f"OK Login successful for {username}")
            return True
        else:
            print(f"FAIL Login failed for {username} (Status: {response.status_code})")
            return False

    def logout(self):
        """Logout current user"""
        response = self.session.get(f"{self.base_url}/auth/logout")
        return response.status_code == 302

    def test_page_access(self, url, expected_status=200):
        """Test access to a specific page"""
        response = self.session.get(f"{self.base_url}{url}", allow_redirects=False)
        return response.status_code, response

    def test_admin_role(self):
        """Test admin user capabilities"""
        print("\n" + "="*60)
        print("TESTING ADMIN ROLE (admin / admin123)")
        print("="*60)

        if not self.login("admin", "admin123"):
            return False

        # Test admin dashboard access
        status, response = self.test_page_access("/admin/dashboard")
        if status == 200:
            print("OK Admin can access dashboard")
        else:
            print(f"FAIL Admin dashboard access denied (Status: {status})")

        # Test user management access
        status, response = self.test_page_access("/admin/users")
        if status == 200:
            print("OK Admin can access user management")
        else:
            print(f"FAIL Admin user management access denied (Status: {status})")

        # Test user edit page access (user ID 5)
        status, response = self.test_page_access("/admin/users/5/edit")
        if status == 200:
            print("OK Admin can access user edit page")
        elif status == 500:
            print(f"FAIL Admin user edit has internal server error (Status: {status})")
            print(f"Response content: {response.text[:500]}")
        else:
            print(f"FAIL Admin user edit access denied (Status: {status})")

        # Test user creation page access
        status, response = self.test_page_access("/admin/users/create")
        if status == 200:
            print("OK Admin can access user creation page")
        else:
            print(f"FAIL Admin user creation access denied (Status: {status})")

        # Test whitelist management page access
        status, response = self.test_page_access("/admin/whitelist")
        if status == 200:
            print("OK Admin can access whitelist management page")
        else:
            print(f"FAIL Admin whitelist management access denied (Status: {status})")

        # Test system info access
        status, response = self.test_page_access("/admin/system_info")
        if status == 200:
            print("OK Admin can access system info")
        else:
            print(f"FAIL Admin system info access denied (Status: {status})")

        # Test patient creation restriction
        status, response = self.test_page_access("/")
        if status == 302 or 'administrators cannot create' in response.text.lower():
            print("OK Admin correctly restricted from patient creation")
        else:
            print("FAIL Admin not restricted from patient creation")

        self.logout()
        return True

    def test_regular_user_role(self):
        """Test regular user capabilities"""
        print("\n" + "="*60)
        print("TESTING REGULAR USER ROLE (user1 / user123)")
        print("="*60)

        if not self.login("user1", "user123"):
            return False

        # Test patient creation access
        status, response = self.test_page_access("/")
        if status == 200 and 'patient' in response.text.lower():
            print("OK Regular user can access patient creation")
        else:
            print(f"FAIL Regular user patient creation access denied (Status: {status})")

        # Test patient list access
        status, response = self.test_page_access("/patients")
        if status == 200:
            print("OK Regular user can access patient list")
        else:
            print(f"FAIL Regular user patient list access denied (Status: {status})")

        # Test admin area restriction
        status, response = self.test_page_access("/admin/dashboard")
        if status == 302:
            print("OK Regular user correctly restricted from admin area")
        else:
            print(f"FAIL Regular user admin restriction failed (Status: {status})")

        # Test creating a patient
        patient_data = {
            'ipp': '12345678',
            'first_name': 'Test',
            'last_name': 'Patient',
            'birth_date': '1990-01-01',
            'sex': 'M'
        }

        response = self.session.post(f"{self.base_url}/", data=patient_data, allow_redirects=False)
        if response.status_code in [200, 302]:
            print("OK Regular user can create patients")
        else:
            print(f"FAIL Regular user patient creation failed (Status: {response.status_code})")

        self.logout()
        return True

    def test_principal_investigator_role(self):
        """Test principal investigator capabilities"""
        print("\n" + "="*60)
        print("TESTING PRINCIPAL INVESTIGATOR ROLE (pi_user / pi123)")
        print("="*60)

        if not self.login("pi_user", "pi123"):
            return False

        # Test patient creation access
        status, response = self.test_page_access("/")
        if status == 200 and 'patient' in response.text.lower():
            print("OK PI can access patient creation")
        else:
            print(f"FAIL PI patient creation access denied (Status: {status})")

        # Test patient list access
        status, response = self.test_page_access("/patients")
        if status == 200:
            print("OK PI can access patient list")
            # Check if PI can see all patients or has special privileges
            if 'principal investigator' in response.text.lower() or len(response.text) > 2000:
                print("OK PI appears to have enhanced patient visibility")
            else:
                print("INFO PI has standard patient visibility")
        else:
            print(f"FAIL PI patient list access denied (Status: {status})")

        # Test admin area restriction (PI should not have admin access)
        status, response = self.test_page_access("/admin/dashboard")
        if status == 302:
            print("OK PI correctly restricted from admin area")
        else:
            print(f"FAIL PI admin restriction failed (Status: {status})")

        # Test creating a patient
        patient_data = {
            'ipp': '87654321',
            'first_name': 'PI',
            'last_name': 'Patient',
            'birth_date': '1985-05-15',
            'sex': 'F'
        }

        response = self.session.post(f"{self.base_url}/", data=patient_data, allow_redirects=False)
        if response.status_code in [200, 302]:
            print("OK PI can create patients")
        else:
            print(f"FAIL PI patient creation failed (Status: {response.status_code})")

        self.logout()
        return True

    def test_authentication_flows(self):
        """Test authentication for all user types"""
        print("\n" + "="*60)
        print("TESTING AUTHENTICATION FLOWS")
        print("="*60)

        test_credentials = [
            ("admin", "admin123", "Admin"),
            ("user1", "user123", "Regular User"),
            ("pi_user", "pi123", "Principal Investigator"),
            ("test_admin", "test123", "Admin"),
            ("test_user", "test123", "Regular User")
        ]

        for username, password, role in test_credentials:
            if self.login(username, password):
                print(f"OK {role} authentication successful")
                if self.logout():
                    print(f"OK {role} logout successful")
                else:
                    print(f"WARN {role} logout issue")
            else:
                print(f"FAIL {role} authentication failed")

    def test_access_boundaries(self):
        """Test access control boundaries"""
        print("\n" + "="*60)
        print("TESTING ACCESS CONTROL BOUNDARIES")
        print("="*60)

        # Test unauthorized access
        print("\n> Testing unauthorized access...")
        status, response = self.test_page_access("/")
        if status == 302:
            print("OK Unauthorized user redirected to login")
        else:
            print(f"FAIL Unauthorized access allowed (Status: {status})")

        status, response = self.test_page_access("/admin/dashboard")
        if status == 302:
            print("OK Unauthorized admin access blocked")
        else:
            print(f"FAIL Unauthorized admin access allowed (Status: {status})")

        # Test invalid login
        print("\n> Testing invalid credentials...")
        response = self.session.post(f"{self.base_url}/auth/login", data={
            'username': 'nonexistent',
            'password': 'wrongpass',
            'auth_method': 'local'
        }, allow_redirects=False)

        if response.status_code != 302:
            print("OK Invalid credentials rejected")
        else:
            print("FAIL Invalid credentials accepted")

    def run_all_tests(self):
        """Run all role tests"""
        print("CARPEM Oncocentre - Comprehensive Role Testing via HTTP")
        print("=" * 60)

        try:
            # Test basic connectivity
            response = requests.get(f"{self.base_url}/auth/login", timeout=5)
            if response.status_code != 200:
                print("FAIL Cannot connect to application")
                return False
            print("OK Application is accessible")

            # Run all tests
            self.test_authentication_flows()
            self.test_admin_role()
            self.test_regular_user_role()
            self.test_principal_investigator_role()
            self.test_access_boundaries()

            print("\n" + "="*60)
            print("COMPREHENSIVE ROLE TESTING COMPLETED")
            print("="*60)
            print("\nFor manual testing, visit: http://localhost:5000")
            print("Available test accounts:")
            print("- admin / admin123 (Admin)")
            print("- user1 / user123 (Regular User)")
            print("- pi_user / pi123 (Principal Investigator)")

            return True

        except requests.ConnectionError:
            print("FAIL Cannot connect to application. Make sure it's running on localhost:5000")
            return False
        except Exception as e:
            print(f"FAIL Test error: {e}")
            return False

if __name__ == '__main__':
    tester = RoleTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)