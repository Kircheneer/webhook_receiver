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
1. Configure webhooks in Netbox with the same SECRET and point them to the url of this application
1. Add your tasks to the module user_tasks, make sure they are decorated with the correct model/action
1. Run the receiver with `docker-compose up`
1. Make a change in Netbox corresponding to the webhooks and tasks you configured 

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