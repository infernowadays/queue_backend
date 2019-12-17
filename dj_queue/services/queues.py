from django.contrib.auth.models import User

from dj_queue.models import Queue, Invitation
from dj_queue.services.notifications import send_notification_for


class CreateQueue:
    def __init__(self, data, owner):
        self.data=data
        self.owner=owner

    def execute(self):
        queue = Queue.objects.create(
            name=self.data['name'],
            description=self.data['description'],
            owner=self.owner
        )
        self._create_invitations(queue)
        return queue

    def _create_invitations(self, queue):
        for invitation in self.data['invitations']:
            found_users = list(User.objects.filter(username=invitation['login']))
            if len(found_users) > 0 and found_users[0] != self.owner:
                created_invitation = Invitation.objects.create(
                    queue=queue,
                    user=found_users[0]
                )
                send_notification_for(created_invitation)
