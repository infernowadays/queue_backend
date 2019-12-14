from firebase_admin import messaging


def send_notification_for(invitation):
    if not hasattr(invitation.user, 'notificationreceiverinfo'):
        return

    user_token = invitation.user.notificationreceiverinfo.notifications_token
    message = messaging.Message(
        token=user_token,
        data={
            'invitation_id': invitation.id,
            'queue_name': invitation.queue.name
        }
    )
    messaging.send(message)
    invitation.notifications_send += 1
    invitation.save()
