import hmac
import importlib
import logging
import pkgutil

from celery import Celery
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseSettings

from webhook_receiver.task_registry import RootTaskRegistry

logging.basicConfig()
logger = logging.getLogger(__file__)


class Settings(BaseSettings):
    secret: str = ""
    encoding: str = "utf-8"
    digestmod: str = "sha512"
    plugin_prefix: str = "nbintegrate_"
    celery_broker: str = "redis://redis:6379"
    celery_backend: str = ""


app = FastAPI(title=__file__)
settings = Settings()
celery: Celery = Celery(
    __file__, broker=settings.celery_broker, backend=settings.celery_backend
)
registry: RootTaskRegistry = RootTaskRegistry(celery=celery)


def verify_hmac(
    body: bytes,
    hexdigest: str,
    secret: str = settings.secret,
    encoding: str = settings.encoding,
    digestmod: str = settings.digestmod,
) -> bool:
    computed_hexdigest = hmac.new(
        secret.encode(encoding), body, digestmod=digestmod
    ).hexdigest()
    return hexdigest == computed_hexdigest


@app.post("/netbox")
async def receive(request: Request) -> None:
    """
    Receive a webhook from Netbox.
    :param model: The model that triggered the webhook.
    :param action: The action that triggered the webhook.
    :param request: The request that is the webhook.
    """
    body = await request.body()
    hexdigest = request.headers["X-Hook-Signature"]
    if not verify_hmac(body, hexdigest):
        raise HTTPException(status_code=403, detail="Shared secret mismatch.")
    await registry.execute(request)


# Discover plugins by name
discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg in pkgutil.iter_modules()
    if name.startswith(settings.plugin_prefix)
}

# Register the plugins in the root registry
for name, plugin_module in discovered_plugins.items():
    logger.info(f"Found plugin {name}.")
    try:
        registry.register_plugin(plugin_module.plugin_task_registry)
    except AttributeError:
        logger.error(
            f'Plugin {name} does not have a member called "plugin_task_registry". '
            "Not loading plugin."
        )
