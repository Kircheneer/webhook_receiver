"""
Implement your own tasks here.

Always put the celery decorator below the registry one
because the registry relies on its input being callable.
"""
import logging
from typing import Any

from webhook_receiver import celery, registry

__all__ = ['example_create_tenant']

logging.basicConfig()
logger = logging.getLogger(__file__)


#####################################
# Example, feel free to delete this #
#####################################
@registry.register(model="tenant", action="create")
@celery.task
def example_create_tenant(request: Any) -> None:
    """
    Example that fires on /tenant/create.
    :param request: The result of the request.json() call on the original request.
    """
    logger.warning(f"Tenant {request['data']['name']} was created.")
