# Photo-editing-ai-be

# Dependencies
    python==3.7
    Django rest==3.14
    Celery
    Web socket
    channel
    Aws (boto client)==1.23.10
    Google authentication


# Virtualenv modules installation 

    python3.7 -m venv venv
    source venv/bin/activate

# Install requirements

    pip install -r requirements.txt

# Production Server

For Celery Setup local Redis server


# For Local setup

<!-- Venv:

    python3.7 -m venv venv
    source venv/bin/activate -->

Django:

    python3 manage.py makemigrations;
    python3 manage.py migrate;
    python3 manage.py loaddata subscriptions.json;
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