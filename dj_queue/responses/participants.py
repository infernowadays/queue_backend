from django.http import JsonResponse


def anon_created(anon_participant):
    queue_participation = anon_participant.queueparticipation_set.all()[0]

    return JsonResponse({
        'id': anon_participant.id,
        'name': anon_participant.name,
        'position': queue_participation.position
    }, status=201)
