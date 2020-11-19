import hmac
import logging

from celery import Celery
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseSettings

from webhook_receiver.task_registry import TaskRegistry

logging.basicConfig()
logger = logging.getLogger(__file__)


class Settings(BaseSettings):
    secret: str
    encoding: str = 'utf-8'
    digestmod: str = 'sha512'


app = FastAPI(title='__file__')
celery = Celery('webhook_receiver', broker='redis://redis:6379')
registry = TaskRegistry(app)
settings = Settings()


def verify_hmac(
        body: bytes,
        hexdigest: str,
        secret: str = settings.secret,
        encoding: str = settings.encoding,
        digestmod: str = settings.digestmod
) -> bool:
    computed_hexdigest = hmac.new(
        secret.encode(encoding),
        body,
        digestmod=digestmod
    ).hexdigest()
    return hexdigest == computed_hexdigest


@app.post('/{model}/{action}')
async def netbox(model: str, action: str, request: Request):
    body = await request.body()
    hexdigest = request.headers['X-Hook-Signature']
    if not verify_hmac(body, hexdigest):
        raise HTTPException(
            status_code=403, detail='Shared secret mismatch.'
        )
    await registry.execute(request, model, action)


# Ensure all the tasks are registered properly in both the worker and the web process
from webhook_receiver.tasks import *  # noqa: E402
