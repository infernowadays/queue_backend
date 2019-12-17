from django.http import JsonResponse


def created(created_q):
    return JsonResponse({
        'id': created_q.id,
        'name': created_q.name,
        'description': created_q.description
    }, status=201)
