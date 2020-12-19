# Webhook Receiver

A webhook receiver implemented with the Netbox IPAM/DCIM software in mind as the target platform.

## Dependencies

You need the following:

- Docker and docker-compose installed
- A working Netbox instance with working webhooks

## Quickstart

1. Clone this repository with `git clone https://github.com/Kircheneer/webhook_receiver.git; cd webhook_receiver`
1. Configure environment variables, most importantly the SECRET, in env/web.env
   or in any other way supported by docker-compose
1. Configure a webhook in Netbox with a matching secret and point it to `/netbox`
1. Write your tasks using a  `PluginTaskRegistry` instance called `plugin_task_registry` in a importable module
   prefixed with `nbintegrate_` so they will be picked up by the root registry
1. Run the receiver with `docker-compose up`
1. Make a change in Netbox corresponding to the tasks you configured and watch them be executed

## Configuration

Configuration is done via environment variables:

| Variable       | Purpose                                              | Default            |
|----------------|------------------------------------------------------|--------------------|
| SECRET         | The shared secret entered for the webhooks in Netbox |                    |
| ENCODING       | The encoding of the secret used for the HMAC         | utf-8              |
| DIGESTMOD      | The hash function used for the HMAC                  | sha512             |
| TASKS_MODULE   | The module to import the tasks from                  | user_tasks         |
| CELERY_BROKER  | The URL for the celery broker                        | redis://redis:6379 |
| CELERY_BACKEND | The URL for the celery backen storage                |                    |
