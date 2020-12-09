"""
Implement your own tasks here.

Always put the celery decorator below the registry one
because the registry relies on its input being callable.
"""
import logging
from typing import Any

from webhook_receiver.task_registry import PluginTaskRegistry

logging.basicConfig()
logger = logging.getLogger(__file__)

# An object with this exact name has to be present in every plugin.
# It is automatically imported
plugin_task_registry = PluginTaskRegistry(name="Example")


#####################################
# Example, feel free to delete this #
#####################################
@plugin_task_registry.register(model="tenant", event="created")
def example_create_tenant(request: Any) -> None:
    """
    Example that fires on /tenant/create.
    :param request: The result of the request.json() call on the original request.
    """
    logger.warning(f"Tenant {request['data']['name']} was created.")
