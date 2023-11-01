from django.urls import path
from .views import (ProcessImage)

urlpatterns = [
    path("process-image", ProcessImage.as_view()),
]
