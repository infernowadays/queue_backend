from django.http import JsonResponse
from django.views.generic import View


class What(View):
    def post(self, request):
        return JsonResponse({'access_token': request.POST.get('code')})
