from tau2.registry import registry
from tau2_enhanced.environments.logging_environment import LoggingEnvironment
from tau2.domains.airline.environment import get_tasks as airline_domain_get_tasks

def get_enhanced_airline_environment(db=None, solo_mode=False):
    from tau2.domains.airline.environment import get_environment
    original_env = get_environment(db=db, solo_mode=solo_mode)
    return LoggingEnvironment(
        domain_name=original_env.domain_name,
        policy=original_env.policy,
        tools=original_env.tools,
        user_tools=original_env.user_tools
    )

def register_enhanced_domains():
    """Register enhanced domains with the tau2 registry"""
    registry.register_domain(get_enhanced_airline_environment, "airline_enhanced")
    registry.register_tasks(airline_domain_get_tasks, "airline_enhanced")

# Register the domains when this module is imported
register_enhanced_domains()