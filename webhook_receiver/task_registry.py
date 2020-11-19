import logging

from fastapi import FastAPI, Request

logging.basicConfig()
logger = logging.getLogger(__file__)


class TaskRegistry:
    """
    Registry for tasks to be executed when model and action conditions are met.
    """
    def __init__(self, app: FastAPI):
        self.app = app
        self.registry = {}

    def register(
            self,
            model: str,
            action: str
    ):
        """
        Decorator to register tasks in the registry.
        :param model: Model to register the task for.
        :param action: Action to register the task for.
        :return: A decorator adding the decorated function to the registry.
        """
        if model not in self.registry:
            self.registry[model] = {}
        if action not in self.registry[model]:
            self.registry[model][action] = set()

        def decorator(function):
            self.registry[model][action].add(function)
            return function

        return decorator

    async def execute(self, request: Request, model: str, action: str):
        """
        Executes those tasks in the registry that are assigned to the model and the action.
        :param request: The request to pass into the task.
        :param model: The model to filter the tasks.
        :param action: The action to filters the tasks.
        :return:
        """
        try:
            tasks_to_run = self.registry[model][action]
        except KeyError:
            logger.warning(f'No tasks configured for model {model} and action {action}.')
            return
        for f in tasks_to_run:
            f.delay(await request.json())
