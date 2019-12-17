from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from .views import *
from token_auth import views

urlpatterns = [
    path('health', csrf_exempt(HealthView.as_view())),

    path('auth', csrf_exempt(views.LoginView.as_view())),
    path('users', csrf_exempt(views.SignUpView.as_view())),

    path('me', csrf_exempt(AccountView.as_view())),

    path('queues', csrf_exempt(QueuesView.as_view())),
    path('queues/<int:queue_id>', csrf_exempt(QueueView.as_view())),
    path('queue/<int:queue_id>/member/<int:member_id>', csrf_exempt(EditQueueMember.as_view())),
    path('queues/<int:queue_id>/members', csrf_exempt(QueueMembersView.as_view())),
    path('queues/<int:queue_id>/members/<int:member_id>', csrf_exempt(DeleteMemberFromQueueView.as_view())),

    path('invitations', csrf_exempt(InviteUsersView.as_view())),
    path('invitations/<int:invitation_id>', csrf_exempt(GetInvitationView.as_view())),
    path('invitations/<int:invitation_id>/responses', csrf_exempt(InvitationResponseView.as_view())),

    path('clear/memberships', csrf_exempt(ClearMemberships.as_view())),
    path('clear/users', csrf_exempt(ClearUsers.as_view())),
    path('clear/queues', csrf_exempt(ClearQueues.as_view())),
    path('clear/tokens', csrf_exempt(ClearTokens.as_view())),
]