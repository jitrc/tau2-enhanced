"""
Automatic registration of enhanced versions of all tau2 domains.

This module provides automatic registration of enhanced domains that wrap
original tau2 domains with LoggingEnvironment for detailed logging capabilities.
"""

from typing import Optional, Dict, Any, Callable
from loguru import logger

from tau2.registry import registry
from tau2_enhanced.environments.logging_environment import LoggingEnvironment


class EnhancedDomainRegistry:
    """Registry for enhanced domain variants with automatic discovery."""

    def __init__(self):
        self._enhanced_domains = {}
        self._original_constructors = {}

    def register_enhanced_domain(
        self,
        domain_name: str,
        original_get_environment: Callable,
        original_get_tasks: Optional[Callable] = None,
        enhanced_suffix: str = "_enhanced"
    ) -> None:
        """
        Register an enhanced version of a domain.

        Args:
            domain_name: Original domain name (e.g., 'airline')
            original_get_environment: Original domain environment constructor
            original_get_tasks: Original domain tasks getter (optional)
            enhanced_suffix: Suffix for enhanced domain name
        """
        enhanced_domain_name = f"{domain_name}{enhanced_suffix}"

        def get_enhanced_environment(*args, **kwargs) -> LoggingEnvironment:
            """Create enhanced environment wrapper."""
            try:
                # Get the original environment
                original_env = original_get_environment(*args, **kwargs)

                # Wrap with LoggingEnvironment
                enhanced_env = LoggingEnvironment(
                    domain_name=original_env.domain_name,
                    policy=original_env.policy,
                    tools=original_env.tools,
                    user_tools=getattr(original_env, 'user_tools', None)
                )

                logger.debug(f"Created enhanced environment for domain '{domain_name}'")
                return enhanced_env

            except Exception as e:
                logger.error(f"Failed to create enhanced environment for {domain_name}: {e}")
                raise

        try:
            # Check if already registered to avoid double registration
            if enhanced_domain_name not in registry.get_domains():
                # Register enhanced domain
                registry.register_domain(get_enhanced_environment, enhanced_domain_name)
                logger.info(f"Registered enhanced domain: {enhanced_domain_name}")
            else:
                logger.debug(f"Enhanced domain {enhanced_domain_name} already registered, skipping")

            # Register tasks if provided
            if original_get_tasks and enhanced_domain_name not in registry.get_task_sets():
                registry.register_tasks(original_get_tasks, enhanced_domain_name)
                logger.info(f"Registered enhanced tasks: {enhanced_domain_name}")
            elif original_get_tasks:
                logger.debug(f"Enhanced tasks {enhanced_domain_name} already registered, skipping")

            # Store for reference
            self._enhanced_domains[enhanced_domain_name] = {
                'original_domain': domain_name,
                'enhanced_constructor': get_enhanced_environment,
                'original_constructor': original_get_environment,
                'tasks_getter': original_get_tasks
            }
            self._original_constructors[domain_name] = original_get_environment

        except Exception as e:
            logger.error(f"Failed to register enhanced domain {enhanced_domain_name}: {e}")
            raise

    def register_all_available_domains(self) -> Dict[str, str]:
        """
        Automatically discover and register enhanced versions of all available domains.

        Returns:
            Dict mapping original domain names to enhanced domain names
        """
        registered_domains = {}

        # Import domain constructors with error handling
        domain_imports = {
            'airline': self._import_airline_domain,
            'retail': self._import_retail_domain,
            'telecom': self._import_telecom_domain,
            'mock': self._import_mock_domain
        }

        for domain_name, import_func in domain_imports.items():
            try:
                constructors = import_func()
                if constructors:
                    get_environment = constructors.get('get_environment')
                    get_tasks = constructors.get('get_tasks')

                    if get_environment:
                        self.register_enhanced_domain(
                            domain_name=domain_name,
                            original_get_environment=get_environment,
                            original_get_tasks=get_tasks
                        )
                        registered_domains[domain_name] = f"{domain_name}_enhanced"

            except Exception as e:
                logger.warning(f"Could not register enhanced domain for {domain_name}: {e}")
                continue

        logger.info(f"Successfully registered {len(registered_domains)} enhanced domains: {list(registered_domains.values())}")
        return registered_domains

    def _import_airline_domain(self) -> Optional[Dict[str, Callable]]:
        """Import airline domain constructors."""
        try:
            from tau2.domains.airline.environment import get_environment, get_tasks
            return {'get_environment': get_environment, 'get_tasks': get_tasks}
        except ImportError as e:
            logger.warning(f"Could not import airline domain: {e}")
            return None

    def _import_retail_domain(self) -> Optional[Dict[str, Callable]]:
        """Import retail domain constructors."""
        try:
            from tau2.domains.retail.environment import get_environment, get_tasks
            return {'get_environment': get_environment, 'get_tasks': get_tasks}
        except ImportError as e:
            logger.warning(f"Could not import retail domain: {e}")
            return None

    def _import_telecom_domain(self) -> Optional[Dict[str, Callable]]:
        """Import telecom domain constructors."""
        try:
            from tau2.domains.telecom.environment import (
                get_environment_manual_policy as get_environment,
                get_tasks
            )
            return {'get_environment': get_environment, 'get_tasks': get_tasks}
        except ImportError as e:
            logger.warning(f"Could not import telecom domain: {e}")
            return None

    def _import_mock_domain(self) -> Optional[Dict[str, Callable]]:
        """Import mock domain constructors."""
        try:
            from tau2.domains.mock.environment import get_environment, get_tasks
            return {'get_environment': get_environment, 'get_tasks': get_tasks}
        except ImportError as e:
            logger.warning(f"Could not import mock domain: {e}")
            return None

    def get_enhanced_domains(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered enhanced domains."""
        return self._enhanced_domains.copy()

    def is_enhanced_domain(self, domain_name: str) -> bool:
        """Check if a domain name is an enhanced domain."""
        return domain_name in self._enhanced_domains

    def get_original_domain_name(self, enhanced_domain_name: str) -> Optional[str]:
        """Get the original domain name for an enhanced domain."""
        domain_info = self._enhanced_domains.get(enhanced_domain_name)
        return domain_info['original_domain'] if domain_info else None


# Create global registry instance
enhanced_domain_registry = EnhancedDomainRegistry()


def register_all_enhanced_domains() -> Dict[str, str]:
    """
    Convenience function to register all available enhanced domains.

    Returns:
        Dict mapping original domain names to enhanced domain names
    """
    return enhanced_domain_registry.register_all_available_domains()


def register_enhanced_domain(
    domain_name: str,
    original_get_environment: Callable,
    original_get_tasks: Optional[Callable] = None
) -> None:
    """
    Convenience function to register a single enhanced domain.

    Args:
        domain_name: Original domain name
        original_get_environment: Original environment constructor
        original_get_tasks: Original tasks getter (optional)
    """
    enhanced_domain_registry.register_enhanced_domain(
        domain_name=domain_name,
        original_get_environment=original_get_environment,
        original_get_tasks=original_get_tasks
    )


def get_enhanced_domains_info() -> Dict[str, Dict[str, Any]]:
    """Get information about all registered enhanced domains."""
    return enhanced_domain_registry.get_enhanced_domains()


def is_enhanced_domain(domain_name: str) -> bool:
    """Check if a domain name is an enhanced domain."""
    return enhanced_domain_registry.is_enhanced_domain(domain_name)


# Automatic registration when module is imported
if __name__ != "__main__":
    try:
        registered = register_all_enhanced_domains()
        if registered:
            logger.info(f"Enhanced domain registration completed. Available enhanced domains: {list(registered.values())}")
        else:
            logger.warning("No enhanced domains were registered. Check tau2-bench installation.")
    except Exception as e:
        logger.error(f"Error during automatic enhanced domain registration: {e}")