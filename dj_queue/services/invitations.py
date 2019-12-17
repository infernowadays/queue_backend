from dj_queue.enums import Decision
from dj_queue.services.queues import append_user_to_queue


class AcceptInvitation:
    def __init__(self, invitation, data):
        self.invitation = invitation
        self.data = data

    def execute(self):
        if self.invitation.decision is not None:
            return

        self.invitation.decision = self.data['decision']
        self.invitation.save()
        if Decision(self.data['decision']) == Decision.ACCEPT:
            append_user_to_queue(self.invitation.queue, self.invitation.user)
