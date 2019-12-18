from django.http import JsonResponse


def anon_participant_created(anon_participant):
    queue_participation = anon_participant.queueparticipation_set.all()[0]

    return JsonResponse({
        'id': anon_participant.id,
        'name': anon_participant.name,
        'position': queue_participation.position
    }, status=201)


def participation_info(participation):
    if participation.user is not None:
        name = participation.user.name
    else:
        name = participation.anon_participant.name

    return JsonResponse({
        'id': participation.id,
        'name': name,
        'position': participation.position
    }, status=200)
