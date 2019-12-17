from django.contrib.auth.models import User
from django.db import transaction

from dj_queue.models import Queue, Invitation, AnonParticipant, QueueParticipation
from dj_queue.services.notifications import send_notification_for


class CreateQueue:
    def __init__(self, data, owner):
        self.data = data
        self.owner = owner

    def execute(self):
        queue = Queue.objects.create(
            name=self.data['name'],
            description=self.data['description'],
            owner=self.owner
        )
        append_user_to_queue(queue, self.owner)
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


class AddMemberToQueue:
    def __init__(self, queue, data):
        self.queue = queue
        self.data = data

    def execute(self):
        name = self.data['name']
        position = self.data['position']

        participants = list(self.queue.queueparticipation_set.all())
        if position > len(participants):
            position = len(participants)

        with transaction.atomic():
            anon_participant = AnonParticipant.objects.create(name=name)
            if position < len(participants):
                for participant in filter(lambda it: it.position >= position, participants):
                    participant.position += 1
                    participant.save()
            QueueParticipation.objects.create(
                queue=self.queue,
                anon_participant=anon_participant,
                position=position
            )

        return anon_participant


def append_user_to_queue(queue, user):
    if len(queue.queueparticipation_set.filter(user=user)) < 1:
        QueueParticipation.objects.create(
            queue=queue,
            user=user,
            position=len(queue.queueparticipation_set.all())
        )
