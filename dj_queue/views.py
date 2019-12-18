from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from dj_queue.forms.InvitationResponseForm import InvitationResponseForm
from dj_queue.forms.NewQueueMemberForm import NewQueueMemberForm
from dj_queue.forms.PutQueueMemberForm import PutQueueMemberForm
from .models import Queue, Invitation, QueueParticipation
from dj_queue.forms.QueueForm import QueueForm

import dj_queue.services.account as acc_service
import dj_queue.services.queues as q_service
import dj_queue.services.invitations as inv_service

import dj_queue.responses.queues as q_resps
import dj_queue.responses.participants as qp_resps
import dj_queue.responses.errors as errresp
from dj_queue.responses.general import no_content


class HealthView(APIView):
    permission_classes = (AllowAny,)

    def get(self, _):
        return HttpResponse(status=200)


class AccountView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def patch(self, request):
        acc_service.UpdateAccount(request.user, request.data).execute()
        return no_content()


class QueuesView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        queue_form = QueueForm(request.data, request.FILES)
        if not queue_form.is_valid():
            return errresp.bad_form(queue_form.errors)
        created_q = q_service.CreateQueue(queue_form.cleaned_data, request.user).execute()
        return q_resps.created(created_q)

    def get(self, request):
        return q_resps.my_queues(
            list(q_service.find_user_queues(request.user)),
            request.user
        )


class QueueView(APIView):
    def get(self, _, queue_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return errresp.not_found(f'queue with id={queue_id} wan\'t found')

        return q_resps.queue_info(queue)

    def delete(self, request, queue_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return errresp.not_found(f'queue with id={queue_id} wan\'t found')

        q_service.LeaveQueue(queue=queue, user=request.user).execute()
        return no_content()


class QueueMembersView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    # Add participant to queue
    def post(self, request, queue_id):
        new_member_form = NewQueueMemberForm(request.data, request.FILES)
        if not new_member_form.is_valid():
            return errresp.bad_form(new_member_form.errors)

        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return errresp.not_found(f"queue width id=${queue_id} was not found")

        created_participant = q_service \
            .AddMemberToQueue(queue, new_member_form.cleaned_data).execute()

        return qp_resps.anon_participant_created(created_participant)


class QueueMemberView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request, queue_id, member_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return errresp.not_found(f"queue width id={queue_id} was not found")

        try:
            participation = queue.queueparticipation_set.get(id=member_id)
        except QueueParticipation.DoesNotExist:
            return errresp.not_found(f'no member with id={member_id} in queue with id={queue_id}')

        if queue.owner != request.user:
            return errresp.forbidden()

        q_service.DeleteMemberFromQueue(participation).execute()

        return no_content()

    def put(self, request, queue_id, member_id):
        put_queue_member_form = PutQueueMemberForm(request.data, request.FILES)
        if not put_queue_member_form.is_valid():
            return errresp.bad_form(put_queue_member_form.errors)

        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return errresp.not_found(f"queue width id={queue_id} was not found")

        try:
            participation = queue.queueparticipation_set.get(id=member_id)
        except QueueParticipation.DoesNotExist:
            return errresp.not_found(f'no member with id={member_id} in queue with id={queue_id}')

        q_service.EditQueueMember(participation, put_queue_member_form.cleaned_data).execute()

        return qp_resps.participation_info(participation)


class GetInvitationView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, invitation_id):
        key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        try:
            user_id = Token.objects.get(key=key).user_id
        except Token.DoesNotExist:
            return JsonResponse({'error': 'token does not exist'}, status=404, safe=False)

        try:
            invitation = Invitation.objects.get(id=invitation_id)
        except Invitation.DoesNotExist:
            return JsonResponse({'error': 'invitation does not exist'}, status=404, safe=False)

        if invitation.user_id != user_id:
            return JsonResponse({'error': 'no such invitation'}, status=404, safe=False)

        try:
            queue = Queue.objects.get(id=invitation.queue_id)
        except Queue.DoesNotExist:
            return JsonResponse({'error': 'queue does not exist'}, status=404, safe=False)

        response = {
            'queue': {
                'id': queue.id,
                'name': queue.name,
                'description': queue.description
            }
        }

        return JsonResponse(response, status=200, safe=False)


class InviteUsersView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        try:
            queue_id = self.request.data['queueId']
            invitations = self.request.data['invitations']

            logins = list([])
            for invitation in invitations:
                if invitation.get('login') is None:
                    return JsonResponse({'error': 'invalid syntax'}, status=400, safe=False)

                logins.append(invitation.get('login'))

        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
            return JsonResponse({'error': 'queue does not exist'}, status=404, safe=False)

        for login in logins:
            try:
                member = User.objects.get(username=login)
                try:
                    Invitation.objects.create(queue=queue, member=member)
                except IntegrityError:
                    continue
            except User.DoesNotExist:
                continue

        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class InvitationResponseView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request, invitation_id):
        inv_response_form = InvitationResponseForm(request.data, request.FILES)
        if not inv_response_form.is_valid():
            return errresp.bad_form(inv_response_form.errors)

        try:
            invitation = Invitation.objects.get(id=invitation_id)
        except Invitation.DoesNotExist:
            return errresp.not_found(f'invitation with id=${invitation_id} wasn\'t found')

        if not request.user == invitation.user:
            return errresp.forbidden()

        inv_service.AcceptInvitation(invitation, inv_response_form.cleaned_data).execute()
        return no_content()


class ClearMemberships(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    # def delete(self, request):
    # Membership.objects.all().delete()
    #
    # return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearUsers(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
        User.objects.all().delete()

        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearQueues(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
        Queue.objects.all().delete()

        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearTokens(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def delete(self, request):
        Token.objects.all().delete()

        return JsonResponse({'status': 'Ok'}, status=200, safe=False)
