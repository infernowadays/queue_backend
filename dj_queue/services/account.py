from dj_queue.models import NotificationReceiverInfo


class UpdateAccount:
    def __init__(self, user, data):
        self.user = user
        self.data = data

    def execute(self):
        if 'notificationsToken' in self.data:
            self._set_notifications_token(self.data['notificationsToken'])

        self.user.save()

    def _set_notifications_token(self, token):
        found_entities = NotificationReceiverInfo.objects.filter(user=self.user)
        if len(found_entities) > 0:
            found_entities[0].notifications_token = token
            found_entities[0].save(update_fields=['notifications_token'])
        else:
            NotificationReceiverInfo.objects.create(user=self.user, notifications_token=token)
