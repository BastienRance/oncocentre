#!/usr/bin/env python3
"""
Test whitelist management functionality
"""

import requests
import sys

class WhitelistTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def login_admin(self):
        """Login as admin to test whitelist management"""
        # Get login page for CSRF token
        response = self.session.get(f"{self.base_url}/auth/login")
        if response.status_code != 200:
            print("FAIL Cannot access login page")
            return False

        # Extract CSRF token
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break

        if not csrf_token:
            print("FAIL Cannot extract CSRF token")
            return False

        # Login as admin
        response = self.session.post(f"{self.base_url}/auth/login", data={
            'username': 'admin',
            'password': 'admin123',
            'auth_method': 'local',
            'csrf_token': csrf_token
        }, allow_redirects=False)

        if response.status_code == 302:
            print("OK Admin login successful")
            return True
        else:
            print(f"FAIL Admin login failed (Status: {response.status_code})")
            return False

    def test_whitelist_access(self):
        """Test access to whitelist management page"""
        response = self.session.get(f"{self.base_url}/admin/whitelist")
        if response.status_code == 200:
            print("OK Admin can access whitelist management page")
            return True
        else:
            print(f"FAIL Admin whitelist access denied (Status: {response.status_code})")
            return False

    def test_add_user_to_whitelist(self, username, description="Test user"):
        """Test adding a user to the whitelist"""
        response = self.session.post(f"{self.base_url}/admin/whitelist/add", data={
            'username': username,
            'description': description
        }, allow_redirects=False)

        if response.status_code == 302:  # Redirect after successful add
            print(f"OK Successfully added user '{username}' to whitelist")
            return True
        else:
            print(f"FAIL Failed to add user '{username}' (Status: {response.status_code})")
            return False

    def test_remove_user_from_whitelist(self, username):
        """Test removing a user from the whitelist"""
        response = self.session.get(f"{self.base_url}/admin/whitelist/remove/{username}",
                                  allow_redirects=False)

        if response.status_code == 302:  # Redirect after successful removal
            print(f"OK Successfully removed user '{username}' from whitelist")
            return True
        else:
            print(f"FAIL Failed to remove user '{username}' (Status: {response.status_code})")
            return False

    def test_reactivate_user(self, username):
        """Test reactivating a deactivated user"""
        response = self.session.get(f"{self.base_url}/admin/whitelist/activate/{username}",
                                  allow_redirects=False)

        if response.status_code == 302:  # Redirect after successful activation
            print(f"OK Successfully reactivated user '{username}'")
            return True
        else:
            print(f"FAIL Failed to reactivate user '{username}' (Status: {response.status_code})")
            return False

    def test_migrate_environment(self):
        """Test migrating environment whitelist to database"""
        response = self.session.get(f"{self.base_url}/admin/whitelist/migrate",
                                  allow_redirects=False)

        if response.status_code == 302:  # Redirect after successful migration
            print("OK Successfully triggered environment migration")
            return True
        else:
            print(f"FAIL Environment migration failed (Status: {response.status_code})")
            return False

    def test_authentication_with_database_whitelist(self):
        """Test that authentication uses database whitelist"""
        # Logout first
        self.session.get(f"{self.base_url}/auth/logout")

        # Try to login with a user that should be in the database whitelist
        response = self.session.get(f"{self.base_url}/auth/login")
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrf_token' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break

        if csrf_token:
            response = self.session.post(f"{self.base_url}/auth/login", data={
                'username': 'user1',
                'password': 'user123',
                'auth_method': 'local',
                'csrf_token': csrf_token
            }, allow_redirects=False)

            if response.status_code == 302:
                print("OK Database whitelist authentication working")
                return True
            else:
                print(f"FAIL Database whitelist authentication failed (Status: {response.status_code})")
                return False

        print("FAIL Could not get CSRF token for authentication test")
        return False

    def run_all_tests(self):
        """Run comprehensive whitelist management tests"""
        print("CARPEM Oncocentre - Whitelist Management Testing")
        print("=" * 60)

        try:
            # Test basic connectivity
            response = requests.get(f"{self.base_url}/auth/login", timeout=5)
            if response.status_code != 200:
                print("FAIL Cannot connect to application")
                return False
            print("OK Application is accessible")

            # Login as admin
            if not self.login_admin():
                return False

            # Test whitelist management features
            print("\n> Testing whitelist management access...")
            self.test_whitelist_access()

            print("\n> Testing add user to whitelist...")
            self.test_add_user_to_whitelist("new_test_user", "Added during testing")

            print("\n> Testing remove user from whitelist...")
            self.test_remove_user_from_whitelist("new_test_user")

            print("\n> Testing reactivate user...")
            self.test_reactivate_user("new_test_user")

            print("\n> Testing environment migration...")
            self.test_migrate_environment()

            print("\n> Testing authentication with database whitelist...")
            self.test_authentication_with_database_whitelist()

            print("\n" + "=" * 60)
            print("WHITELIST MANAGEMENT TESTING COMPLETED")
            print("=" * 60)

            return True

        except requests.ConnectionError:
            print("FAIL Cannot connect to application. Make sure it's running on localhost:5000")
            return False
        except Exception as e:
            print(f"FAIL Test error: {e}")
            return False

if __name__ == '__main__':
    tester = WhitelistTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)