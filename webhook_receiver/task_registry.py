import logging
from typing import Callable, Any, List, Dict, Set, Optional

from celery import Task
from fastapi import Request

logging.basicConfig()
logger = logging.getLogger(__file__)


class TaskRegistry:
    """
    Registry for tasks to be executed when model and action conditions are met.
    """

    def __init__(self):
        self.registry: Dict[str, Dict[str, Set[Task]]] = {}

    def register(self, model: str, event: str) -> Callable[[Callable], Callable]:
        """
        Decorator to register tasks in the registry.
        :param model: Model to register the task for.
        :param event: Event to register the task for.
        :return: A decorator adding the decorated function to the registry.
        """
        if model not in self.registry:
            self.registry[model] = {}
        if event not in self.registry[model]:
            self.registry[model][event] = set()

        def decorator(function):
            self.registry[model][event].add(function)
            return function

        return decorator

    async def execute(self, request: Request) -> Optional[List[Any]]:
        """
        Execute tasks in the registry that are assigned to the model and the action.
        :param request: The request to pass into the task.
        :param model: The model to filter the tasks.
        :param action: The action to filters the tasks.
        :return: A (possibly empty) list of task results or None if no tasks ran.
        """
        data = await request.json()
        try:
            tasks_to_run = self.registry[data['model']][data['event']]
        except KeyError:
            logger.warning(
                f"No tasks configured for model {data['model']} and action {data['event']}."
            )
            return None
        return [f.delay(data) for f in tasks_to_run]
