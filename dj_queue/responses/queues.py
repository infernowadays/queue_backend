from django.http import JsonResponse


def created(created_q):
    return JsonResponse({
        'id': created_q.id,
        'name': created_q.name,
        'description': created_q.description
    }, status=201)


def queue_info(queue):
    queue_info_dict = {
        'id': queue.id,
        'name': queue.name,
        'ownerMemberId': queue.owner_id,
        'members': []
    }

    for participation in queue.queueparticipation_set.all():
        participation_info = {
            'id': participation.id,
            'position': participation.position
        }
        if participation.user is not None:
            participation_info['name'] = participation.user.name
        elif participation.anon_participant is not None:
            participation_info['name'] = participation.anon_participant.name
        else:
            raise Exception("empty participant")
        queue_info_dict['members'].append(participation_info)

    return JsonResponse({'queue': queue_info_dict}, status=200)
