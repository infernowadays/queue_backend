from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from .views import CreateQueueView, GetQueuesView, GetQueueInfoView, AddMemberToAQueueView

urlpatterns = [
    path('create', csrf_exempt(CreateQueueView.as_view())),
    path('queues', csrf_exempt(GetQueuesView.as_view())),
    path('queues/<int:queue_id>', csrf_exempt(GetQueueInfoView.as_view())),
    path('queues/<int:queue_id>/member', csrf_exempt(AddMemberToAQueueView.as_view())),

]