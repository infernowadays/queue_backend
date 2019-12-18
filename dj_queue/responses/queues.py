from django.http import JsonResponse


def created(created_q):
    return JsonResponse({
        'id': created_q.id,
        'name': created_q.name,
        'description': created_q.description
    }, status=201)


def my_queues(queues, user):
    result_list = []
    for queue in queues:
        result_list.append({
            'id': queue.id,
            'name': queue.name,
            'description': queue.description,
            'isOwnedByMe': queue.owner == user
        })

    return JsonResponse(result_list, status=200, safe=False)


def queue_info(queue):
    queue_info_dict = {
        'id': queue.id,
        'name': queue.name,
        'members': []
    }

    for participation in sorted(list(queue.queueparticipation_set.all()), key=lambda it: it.position):
        participation_info = {
            'id': participation.id,
            'position': participation.position
        }
        if participation.user is not None:
            participation_info['name'] = participation.user.first_name
            if participation.user == queue.owner:
                queue_info_dict['ownerMemberId'] = participation.id
        elif participation.anon_participant is not None:
            participation_info['name'] = participation.anon_participant.name
        else:
            raise Exception("empty participant")
        queue_info_dict['members'].append(participation_info)

    return JsonResponse(queue_info_dict, status=200)
