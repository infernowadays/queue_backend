from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from .views import What


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('dj_queue.urls')),
    path('social/', include('social_django.urls')),

    path('social/login/token', csrf_exempt(What.as_view())),
]
