import logging
from typing import Callable, Any, List, Dict, Set, Optional, Generic, TypeVar

from celery import Task, Celery
from fastapi import Request

logging.basicConfig()
logger = logging.getLogger(__file__)

# Generic typevar for task registries
T = TypeVar("T")


class _TaskRegistryBase(Generic[T]):
    """
    Base class for all plugin and root task registries.
    """

    def __init__(self):
        self.registry: Dict[str, Dict[str, Set[T]]] = {}

    def _ensure_present(self, model: str, event: str) -> None:
        """
        Ensure the necessary dictionary keys are present
        :param model: Model key to be present.
        :param event: Event key to be present.
        """
        if model not in self.registry:
            self.registry[model] = {}
        if event not in self.registry[model]:
            self.registry[model][event] = set()


class PluginTaskRegistry(_TaskRegistryBase[Callable]):
    """
    Handles plugin task registration.

    Instantiate inside of plugin in order to designate tasks for registration
    in the task registry.
    """

    def __init__(self, name: str):
        """
        :param name: Name of the plugin
        """
        self.name = name
        super(PluginTaskRegistry, self).__init__()

    def register(self, model: str, event: str):
        self._ensure_present(model, event)

        def decorator(function):
            self.registry[model][event].add(function)
            return function

        return decorator


class RootTaskRegistry(_TaskRegistryBase[Task]):
    """
    Registry for tasks to be executed when model and action conditions are met.
    """

    def __init__(self, celery: Celery):
        """
        :param celery: The celery instance of the app.
        """
        self.celery = celery
        super(RootTaskRegistry, self).__init__()

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
            tasks_to_run = self.registry[data["model"]][data["event"]]
        except KeyError:
            logger.warning(
                f"No tasks configured for model {data['model']} "
                f"and action {data['event']}."
            )
            return None
        return [f.delay(data) for f in tasks_to_run]

    def register(self, model: str, event: str) -> Callable[[Callable], Callable]:
        """
        Decorator to register tasks in the registry.
        :param model: Model to register the task for.
        :param event: Event to register the task for.
        :return: A decorator adding the decorated function to the registry.
        """
        self._ensure_present(model, event)

        def decorator(function: Callable):
            task = self.celery.register_task(self.celery.task(function))
            self.registry[model][event].add(task)
            return function

        return decorator

    def register_plugin(self, plugin: PluginTaskRegistry) -> None:
        """
        Register the tasks a plugin has collected with the root registry.
        :param plugin: The plugin.
        """
        logger.info(f"Registering plugin with name {plugin.name}.")
        for model, events in plugin.registry.items():
            for event, tasks in plugin.registry[model].items():
                for task in tasks:
                    # Manually apply decorator
                    self.register(model, event)(task)
