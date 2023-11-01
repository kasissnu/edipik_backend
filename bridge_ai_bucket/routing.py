from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # We use re_path() due to limitations in URLRouter.
    path("celery-results", consumers.CeleryResultConsumer.as_asgi())
]
