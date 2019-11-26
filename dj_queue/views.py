import json
from django.views import View
from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from django.db.models import F
from rest_framework.response import Response
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.core import serializers

from .models import Queue, Membership


class GetQueuesView(View):
    def get(self, request):
        queues = Queue.objects.all().values('id', 'name')
        return JsonResponse(list(queues), status=200, safe=False)


class GetQueueInfoView(View):
    def get(self, request, queue_id):
        queue = Queue.objects.extra(
            select={
                'ownerMemberId': 'owner_id'
            }
        ).values('id', 'name', 'ownerMemberId').get(id=queue_id)
                
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


class CreateQueueView(View):
    def post(self, request):
        name = self.request.POST.get('name')
        queue = Queue.objects.create(name=name)

        return JsonResponse({'id': queue.id, 'name': queue.name}, status=200, safe=False)

        # for user in users:
        #     try:
        #         found_user = User.objects.get(username=user)
        #         queue.user.add(found_user)
        #     except User.DoesNotExist:
        #         return JsonResponse({'error': 'User ' + user + ' does not exist'}, status=404)



class AddMemberToAQueueView(View):
    def post(self, request, queue_id):
        queue = Queue.objects.get(id=queue_id)

        login = self.request.POST.get('login')
        member = User.objects.get(username=login)
        membership = Membership.objects.create(queue=queue, member=member, position=-1)

        return JsonResponse({'id': member.id, 'login': member.username, 'position': membership.position}, status=200, safe=False)
