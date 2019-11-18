from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from .views import CreateQueueView

urlpatterns = [
    path('create', csrf_exempt(CreateQueueView.as_view())),
]