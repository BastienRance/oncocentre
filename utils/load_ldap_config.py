#!/usr/bin/env python3
"""
Script to load LDAP configuration from .ldap_config.env file
This allows secure configuration without committing credentials to git
"""

import os
from dotenv import load_dotenv

def load_ldap_config(config_file='config/.ldap_config.env'):
    """
    Load LDAP configuration from environment file
    
    Args:
        config_file (str): Path to the LDAP config file
        
    Returns:
        bool: True if config loaded successfully, False otherwise
    """
    
    if not os.path.exists(config_file):
        print(f"Warning: LDAP config file {config_file} not found")
        print("LDAP authentication will use default/environment variable settings")
        return False
    
    try:
        # Load environment variables from file
        load_dotenv(config_file)
        
        # Verify critical LDAP settings
        ldap_enabled = os.getenv('LDAP_ENABLED', 'false').lower() == 'true'
        ldap_server = os.getenv('LDAP_SERVER')
        
        if ldap_enabled:
            print(f"✓ LDAP configuration loaded from {config_file}")
            print(f"  - LDAP Enabled: {ldap_enabled}")
            print(f"  - LDAP Server: {ldap_server}")
            print(f"  - LDAP Domain: {os.getenv('LDAP_DOMAIN', 'Not set')}")
            
            if not ldap_server or ldap_server == 'ldap://your-domain-controller.example.com':
                print("Warning: LDAP server appears to be using default/example value")
                print("Please update config/.ldap_config.env with your actual LDAP server settings")
        else:
            print(f"LDAP configuration loaded but LDAP is disabled")
            
        return True
        
    except Exception as e:
        print(f"Error loading LDAP config from {config_file}: {e}")
        return False

if __name__ == '__main__':
    print("CARPEM Oncocentre - LDAP Configuration Loader")
    print("=" * 45)
    load_ldap_config()