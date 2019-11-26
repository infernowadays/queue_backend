from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.views import View
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.http import JsonResponse


class LoginView(View):
    def post(self, request):
        username = request.POST.get("login")
        password = request.POST.get("password")
        
        if username is None or password is None:
            return JsonResponse({'error': 'Please provide both username and password'}, status=400)
        user = authenticate(username=username, password=password)
        
        if not user:
            return JsonResponse({'error': 'Invalid Credentials'}, status=404)
        token, _ = Token.objects.get_or_create(user=user)
        
        return JsonResponse({'token': token.key}, status=200, safe=False)


class SignUpView(View):
    def post(self, request):
        username = request.POST.get("login")
        first_name = request.POST.get("name")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, first_name=first_name, password=password)

        return JsonResponse({'name': user.first_name, 'login': user.username}, status=200, safe=False)

