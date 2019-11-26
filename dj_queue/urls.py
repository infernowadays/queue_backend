from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from .views import CreateQueueView, GetQueuesView, GetQueueInfoView, AddMemberToAQueueView
from token_auth import views

urlpatterns = [
    path('auth', csrf_exempt(views.LoginView.as_view())),
    path('users', csrf_exempt(views.SignUpView.as_view())),

    path('create', csrf_exempt(CreateQueueView.as_view())),
    path('queues', csrf_exempt(GetQueuesView.as_view())),
    path('queues/<int:queue_id>', csrf_exempt(GetQueueInfoView.as_view())),
    path('queues/<int:queue_id>/member', csrf_exempt(AddMemberToAQueueView.as_view())),

]