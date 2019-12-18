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

        participants = list(self.queue.queueparticipation_set.all())
        if 'position' in self.data.keys() and self.data['position'] is not None:
            position = self.data['position']
        else:
            position = len(participants)

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


class EditQueueMember:
    def __init__(self, participation, data):
        self.participation = participation
        self.data = data

    def execute(self):
        all_participations = list(self.participation.queue.queueparticipation_set.all())
        if 'position' in self.data.keys() and self.data['position'] is not None:
            prev_position = self.participation.position
            new_position = self.data['position']
            if new_position > len(all_participations):
                new_position = len(all_participations)

            if self.participation.position == new_position:
                return

            modifier = 1
            filter_l = lambda it: new_position <= it.position < prev_position
            if new_position > prev_position:
                modifier = -1
                filter_l = lambda it: prev_position < it.position <= new_position

            between_prev_and_new_positions = filter(filter_l, all_participations)

            for p in between_prev_and_new_positions:
                p.position += modifier
                p.save()

            self.participation.position = new_position
            self.participation.save()


class DeleteMemberFromQueue:
    def __init__(self, participation):
        self.participation = participation

    def execute(self):
        remove_participation_from_queue(self.participation)


class LeaveQueue:
    def __init__(self, queue, user):
        self.queue = queue
        self.user = user

    def execute(self):
        found = list(self.queue.queueparticipation_set.filter(user=self.user))
        if len(found) < 1:
            return

        remove_participation_from_queue(found[0])


def remove_participation_from_queue(participation):
    user = participation.user
    queue = participation.queue
    all_participations = list(queue.queueparticipation_set.all())
    participations_after = filter(
        lambda it: it.position > participation.position,
        all_participations
    )
    for participation_after in participations_after:
        participation_after.position -= 1
        participation_after.save()

    participation.delete()
    all_participations = list(queue.queueparticipation_set.all())
    if user is not None:  # if real user participation
        sorted_real_user_participations = sorted(
            filter(lambda it: it.user is not None, all_participations),
            key=lambda it: it.position
        )
        if len(sorted_real_user_participations) < 1:
            queue.delete()
        elif queue.owner == user:
            queue.owner = sorted_real_user_participations[0].user
            queue.save()


def append_user_to_queue(queue, user):
    if len(queue.queueparticipation_set.filter(user=user)) < 1:
        QueueParticipation.objects.create(
            queue=queue,
            user=user,
            position=len(queue.queueparticipation_set.all())
        )


def find_user_queues(user):
    participated_queues = set(map(
        lambda it: it.queue,
        set(QueueParticipation.objects.filter(user=user))
    ))
    owned_queues = set(Queue.objects.filter(owner=user))
    return participated_queues.union(owned_queues)
