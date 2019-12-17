from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Queue, Membership, Invitation
from dj_queue.forms.QueueForm import QueueForm
import dj_queue.services.queues as qservice
import dj_queue.services.account as acc_service
import dj_queue.responses.queues as qresp
import dj_queue.responses.errors as errresp
from dj_queue.responses.general import no_content


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
        created_q = qservice.CreateQueue(queue_form.cleaned_data, request.user).execute()
        return qresp.created(created_q)


    def get(self, request):
        key = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        try:
            user_id = Token.objects.get(key=key).user_id
        except Token.DoesNotExist:
            return JsonResponse({'error': 'token does not exist'}, status=404, safe=False)
        
        queues = Queue.objects.filter(owner_id=user_id).values('id', 'name')
        return JsonResponse(list(queues), status=200, safe=False)


class GetQueueInfoView(APIView):
    def get(self, request, queue_id):
        try:
            queue = Queue.objects.extra(
                select={
                    'ownerMemberId': 'owner_id'
                }
            ).values('id', 'name', 'ownerMemberId').get(id=queue_id)
        except Queue.DoesNotExist:
            return JsonResponse({'error': 'does not exist'}, status=404, safe=False)

        queue['members'] = list([])
        member_info = dict({})

        memberships = Membership.objects.filter(queue_id=queue_id)
        for ms in memberships:
            member = User.objects.get(id=ms.member_id)
            member_info['id'] = member.id
            member_info['name'] = member.username    
            member_info['position'] = ms.position 
            queue['members'].append(member_info)           

        return JsonResponse(queue, status=200, safe=False)

    def delete(self, request, queue_id):
        try:
            membership = Membership.objects.filter(queue_id=queue_id).delete()
        except Membership.DoesNotExist:
                return JsonResponse({'error': 'membership does not exist'}, status=404, safe=False)

        try:
            queue = Queue.objects.get(id=queue_id).delete()
        except Queue.DoesNotExist:
                return JsonResponse({'error': 'queue does not exist'}, status=404, safe=False)
        
        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class EditQueueMember(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    
    def put(self, request, queue_id, member_id):
        try:
            position = self.request.data['position']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        if position is None:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        try:
            membership = Membership.objects.get(queue_id=queue_id, member_id=member_id)
        except Membership.DoesNotExist:
            return JsonResponse({'error': 'membership does not exist'}, status=404, safe=False)
        
        membership.position = position
        membership.save()

        try:
            member = User.objects.get(id=member_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'user does not exist'}, status=404, safe=False)

        return JsonResponse({'id': member.id, 'name': member.username, 'position': membership.position}, status=200, safe=False)


class AddMemberToQueueView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    def post(self, request, queue_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
                return JsonResponse({'error': 'queue does not exist'}, status=404, safe=False)
        
        try:
            login = self.request.data['login']
            position = self.request.data['position']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        try:
            member = User.objects.get(username=login)
        except User.DoesNotExist:
            return JsonResponse({'error': 'user does not exist'}, status=404, safe=False)
        
        try:
            membership = Membership.objects.create(queue=queue, member=member, position=position)
        except IntegrityError as e: 
            return JsonResponse({'error': 'user is already in a queue'}, status=500, safe=False)
        
        return JsonResponse({'id': member.id, 'login': member.username, 'position': membership.position}, status=200, safe=False)


class DeleteMemberFromQueueView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    def delete(self, request, queue_id, member_id):
        try:
            queue = Queue.objects.get(id=queue_id)
        except Queue.DoesNotExist:
                return JsonResponse({'error': 'queue does not exist'}, status=404, safe=False)

        try:
            member = User.objects.get(id=member_id)
        except User.DoesNotExist:
                return JsonResponse({'error': 'user does not exist'}, status=404, safe=False)

        try:
            membership = Membership.objects.get(queue_id=queue_id, member_id=member_id).delete()
        except Membership.DoesNotExist:
                return JsonResponse({'error': 'membership does not exist'}, status=404, safe=False)
        
        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class GetInvitationView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

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
    authentication_classes = (TokenAuthentication, )

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


class RespondInvitationView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    def post(self, request, invitation_id):
        try:
            decision = self.request.data['decision']
        except KeyError:
            return JsonResponse({'error': 'provide all the data'}, status=500, safe=False)

        try:
            invitation = Invitation.objects.get(id=invitation_id)
        except Invitation.DoesNotExist:
            return JsonResponse({'error': 'invitation does not exist'}, status=404, safe=False)

        invitation.decision = decision
        invitation.save()

        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearMemberships(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    def delete(self, request):
        Membership.objects.all().delete()
        
        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearUsers(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    
    def delete(self, request):
        User.objects.all().delete()
        
        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearQueues(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    
    def delete(self, request):
        Queue.objects.all().delete()
        
        return JsonResponse({'status': 'Ok'}, status=200, safe=False)


class ClearTokens(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    
    def delete(self, request):
        Token.objects.all().delete()
        
        return JsonResponse({'status': 'Ok'}, status=200, safe=False)