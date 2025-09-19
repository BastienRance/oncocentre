"""
LDAP Authentication module for CARPEM Oncocentre
Provides authentication against Active Directory/LDAP servers
"""

import ldap3
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE
from ldap3.core.exceptions import LDAPException
import os
import logging

logger = logging.getLogger(__name__)

class LDAPAuthenticator:
    """LDAP authentication handler"""
    
    def __init__(self, config=None):
        """Initialize LDAP authenticator with configuration"""
        self.config = config or self._get_default_config()
        self.server = None
        self._initialize_server()
    
    def _get_default_config(self):
        """Get LDAP configuration from environment variables"""
        return {
            'server': os.environ.get('LDAP_SERVER', 'ldap://your-domain-controller.example.com'),
            'port': int(os.environ.get('LDAP_PORT', '389')),
            'use_ssl': os.environ.get('LDAP_USE_SSL', 'false').lower() == 'true',
            'domain': os.environ.get('LDAP_DOMAIN', 'YOURDOMAIN'),
            'base_dn': os.environ.get('LDAP_BASE_DN', 'DC=yourdomain,DC=com'),
            'user_search_base': os.environ.get('LDAP_USER_SEARCH_BASE', 'OU=Users,DC=yourdomain,DC=com'),
            'user_search_filter': os.environ.get('LDAP_USER_SEARCH_FILTER', '(sAMAccountName={username})'),
            'bind_user': os.environ.get('LDAP_BIND_USER', None),  # Optional service account
            'bind_password': os.environ.get('LDAP_BIND_PASSWORD', None),
            'timeout': int(os.environ.get('LDAP_TIMEOUT', '10')),
            'enabled': os.environ.get('LDAP_ENABLED', 'true').lower() == 'true'
        }
    
    def _initialize_server(self):
        """Initialize LDAP server connection"""
        try:
            self.server = Server(
                self.config['server'],
                port=self.config['port'],
                use_ssl=self.config['use_ssl'],
                get_info=ALL,
                connect_timeout=self.config['timeout']
            )
            logger.info(f"LDAP server initialized: {self.config['server']}:{self.config['port']}")
        except Exception as e:
            logger.error(f"Failed to initialize LDAP server: {e}")
            self.server = None
    
    def is_enabled(self):
        """Check if LDAP authentication is enabled"""
        return self.config['enabled'] and self.server is not None
    
    def authenticate(self, username, password):
        """
        Authenticate user against LDAP/Active Directory
        
        Args:
            username (str): Username (without domain)
            password (str): User password
            
        Returns:
            dict: User information if successful, None if failed
        """
        if not self.is_enabled():
            logger.warning("LDAP authentication is disabled")
            return None
        
        if not username or not password:
            logger.warning("Username or password is empty")
            return None
        
        try:
            # Try different authentication methods
            user_info = None
            
            # Method 1: Direct bind with domain\username
            user_info = self._authenticate_domain_user(username, password)
            
            # Method 2: Search and bind (if method 1 fails)
            if not user_info:
                user_info = self._authenticate_search_bind(username, password)
            
            return user_info
            
        except Exception as e:
            logger.error(f"LDAP authentication error for user {username}: {e}")
            return None
    
    def _authenticate_domain_user(self, username, password):
        """Authenticate using domain\\username format"""
        try:
            # Format: DOMAIN\\username or username@domain.com
            domain_username = f"{self.config['domain']}\\\\{username}"
            
            conn = Connection(
                self.server,
                user=domain_username,
                password=password,
                authentication=NTLM,
                auto_bind=True,
                raise_exceptions=True
            )
            
            # Get user information
            user_info = self._get_user_info(conn, username)
            conn.unbind()
            
            logger.info(f"LDAP authentication successful for {username} (domain bind)")
            return user_info
            
        except LDAPException as e:
            logger.debug(f"Domain authentication failed for {username}: {e}")
            return None
    
    def _authenticate_search_bind(self, username, password):
        """Authenticate by searching for user DN then binding"""
        try:
            # First, bind with service account (if configured) or anonymous
            if self.config['bind_user'] and self.config['bind_password']:
                search_conn = Connection(
                    self.server,
                    user=self.config['bind_user'],
                    password=self.config['bind_password'],
                    auto_bind=True
                )
            else:
                search_conn = Connection(self.server, auto_bind=True)
            
            # Search for user
            search_filter = self.config['user_search_filter'].format(username=username)
            search_conn.search(
                search_base=self.config['user_search_base'],
                search_filter=search_filter,
                attributes=['distinguishedName', 'sAMAccountName', 'displayName', 
                           'mail', 'givenName', 'sn', 'memberOf']
            )
            
            if not search_conn.entries:
                logger.warning(f"User {username} not found in LDAP")
                search_conn.unbind()
                return None
            
            # Get user DN
            user_entry = search_conn.entries[0]
            user_dn = user_entry.distinguishedName.value
            search_conn.unbind()
            
            # Now bind with user credentials
            user_conn = Connection(
                self.server,
                user=user_dn,
                password=password,
                auto_bind=True,
                raise_exceptions=True
            )
            
            # Create user info from LDAP attributes
            user_info = {
                'username': username,
                'dn': user_dn,
                'display_name': getattr(user_entry.displayName, 'value', username),
                'email': getattr(user_entry.mail, 'value', ''),
                'first_name': getattr(user_entry.givenName, 'value', ''),
                'last_name': getattr(user_entry.sn, 'value', ''),
                'groups': [group for group in getattr(user_entry.memberOf, 'values', [])],
                'auth_source': 'ldap'
            }
            
            user_conn.unbind()
            logger.info(f"LDAP authentication successful for {username} (search bind)")
            return user_info
            
        except LDAPException as e:
            logger.debug(f"Search bind authentication failed for {username}: {e}")
            return None
    
    def _get_user_info(self, conn, username):
        """Extract user information from LDAP connection"""
        try:
            # Search for current user info
            search_filter = f"(sAMAccountName={username})"
            conn.search(
                search_base=self.config['user_search_base'],
                search_filter=search_filter,
                attributes=['sAMAccountName', 'displayName', 'mail', 
                           'givenName', 'sn', 'memberOf', 'distinguishedName']
            )
            
            if conn.entries:
                entry = conn.entries[0]
                return {
                    'username': username,
                    'dn': getattr(entry.distinguishedName, 'value', ''),
                    'display_name': getattr(entry.displayName, 'value', username),
                    'email': getattr(entry.mail, 'value', ''),
                    'first_name': getattr(entry.givenName, 'value', ''),
                    'last_name': getattr(entry.sn, 'value', ''),
                    'groups': [group for group in getattr(entry.memberOf, 'values', [])],
                    'auth_source': 'ldap'
                }
            
        except Exception as e:
            logger.error(f"Error getting user info for {username}: {e}")
        
        # Fallback user info
        return {
            'username': username,
            'display_name': username,
            'email': '',
            'first_name': '',
            'last_name': '',
            'groups': [],
            'auth_source': 'ldap'
        }
    
    def test_connection(self):
        """Test LDAP server connection"""
        if not self.server:
            return False, "LDAP server not initialized"
        
        try:
            # Try to connect
            conn = Connection(self.server, auto_bind=True)
            conn.unbind()
            return True, "LDAP connection successful"
        except Exception as e:
            return False, f"LDAP connection failed: {e}"
    
    def get_user_groups(self, username):
        """Get user's group memberships"""
        if not self.is_enabled():
            return []
        
        try:
            if self.config['bind_user'] and self.config['bind_password']:
                conn = Connection(
                    self.server,
                    user=self.config['bind_user'],
                    password=self.config['bind_password'],
                    auto_bind=True
                )
            else:
                conn = Connection(self.server, auto_bind=True)
            
            search_filter = self.config['user_search_filter'].format(username=username)
            conn.search(
                search_base=self.config['user_search_base'],
                search_filter=search_filter,
                attributes=['memberOf']
            )
            
            if conn.entries:
                groups = getattr(conn.entries[0].memberOf, 'values', [])
                conn.unbind()
                return groups
            
            conn.unbind()
            return []
            
        except Exception as e:
            logger.error(f"Error getting groups for {username}: {e}")
            return []

# Global LDAP authenticator instance
ldap_auth = LDAPAuthenticator()