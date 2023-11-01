#!/bin/bash
python manage.py makemigrations
python manage.py migrate;
python manage.py loaddata subscriptions.json
hypercorn photo_editing_ai.asgi:application --reload --bind 0.0.0.0:8000
