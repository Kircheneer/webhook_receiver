import logging
from typing import Any

from webhook_receiver import celery, registry

logging.basicConfig()
logger = logging.getLogger(__file__)

__all__ = ['create_tenant']


@registry.register(model='tenant', action='create')
@celery.task
def create_tenant(request: Any) -> None:
    logger.warning(request)
