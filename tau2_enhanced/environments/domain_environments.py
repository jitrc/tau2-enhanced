"""
Enhanced domain environments using the automatic registration system.

This module imports and registers all available enhanced domains automatically.
"""

from loguru import logger
from tau2_enhanced.domain_registration import (
    register_all_enhanced_domains,
    get_enhanced_domains_info,
    is_enhanced_domain
)

# Automatically register all available enhanced domains
try:
    registered_domains = register_all_enhanced_domains()
    logger.info(f"Domain environments module loaded. Enhanced domains available: {list(registered_domains.values())}")
except Exception as e:
    logger.error(f"Error registering enhanced domains: {e}")
    registered_domains = {}

# Export useful functions and data for external use
__all__ = [
    'registered_domains',
    'get_enhanced_domains_info',
    'is_enhanced_domain'
]