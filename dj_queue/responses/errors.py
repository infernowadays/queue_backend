from django.http import JsonResponse


def bad_form(errors):
    response_dict = {
        'success': False,
        'errors': []
    }

    for prop, propErrors in errors.items():
        for propError in propErrors.data:
            path = prop
            if hasattr(propError, 'path') and propError.path is not None:
                path = propError.path
            response_dict['errors'].append({
                'path': path,
                'message': propError.message,
                'code': propError.code
            })

    return JsonResponse(response_dict, status=400)


def not_found(message):
    return JsonResponse({
        'success': False,
        'errors': [{
            'message': message
        }]
    }, status=404)


def forbidden(message='current user doesn\'t have access to requested data'):
    return JsonResponse({
        'success': False,
        'errors': [{
            'message': message
        }]
    }, status=403)