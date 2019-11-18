from django.views import View
from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Queue

class CreateQueueView(View):
    def post(self, request):
        users = self.request.POST.getlist('user')
        queue = Queue.objects.create()

        for user in users:
            try:
                found_user = User.objects.get(username=user)
                queue.user.add(found_user)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User ' + user + ' does not exist'}, status=404)

        return JsonResponse(list(users), status=200, safe=False)
