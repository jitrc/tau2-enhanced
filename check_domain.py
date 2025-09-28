#!/usr/bin/env python3
"""
Domain check script to verify that airline_enhanced domain is registered.
"""

import sys

def check_domain_registration():
    """Check if airline_enhanced domain is available in tau2 registry"""
    try:
        # Import tau2_enhanced first to ensure domain registration
        import tau2_enhanced
        from tau2.registry import registry

        domains = registry.get_domains()
        print(f"Available domains: {domains}")

        if 'airline_enhanced' in domains:
            print("✅ airline_enhanced domain is successfully registered!")
            return True
        else:
            print("❌ airline_enhanced domain is NOT registered")
            return False

    except Exception as e:
        print(f"❌ Error checking domain registration: {e}")
        return False

if __name__ == "__main__":
    success = check_domain_registration()
    sys.exit(0 if success else 1)