# Photo-editing-ai-be

Installation Description

Django

Django Rest framework


# Production Server

For Celery Setup local Redis server


# For Local setup

Venv:

    python3 -m venv venv
    source /opt/data/django/photo-editing-ai-be/venv/bin/activate


Django:

    python3 manage.py makemigrations;
    python3 manage.py migrate;
    python3 manage.py runserver;


Celery worker:

    python3 -m celery -A photo_editing_ai worker -l info

Redis:

    sudo apt-get install redis
    redis-server

Testing-redis

    redis-cli
    ping

Daphne:
We use hypercorn for run application which support asgi functionality

    hypercorn photo_editing_ai.asgi:application --reload