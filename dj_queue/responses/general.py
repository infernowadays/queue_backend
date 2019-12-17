from django.http import JsonResponse, HttpResponse


def no_content():
    return HttpResponse(status=204)
