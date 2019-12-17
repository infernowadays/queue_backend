from django.db import models
from django.contrib.auth.models import User

from dj_queue.enums import Decision


class Queue(models.Model):
    name = models.TextField()
    description = models.TextField(null=True)
    owner = models.ForeignKey(User, null=True, db_constraint=False, on_delete=models.SET_NULL)
    members = models.ManyToManyField(User, related_name='queues', through='Membership')


class Membership(models.Model):
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.IntegerField(default=-1)

    class Meta:
        unique_together = ('queue', 'member',)


class NotificationReceiverInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    notifications_token = models.CharField(null=False, unique=True, max_length=256)


class Invitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    notifications_send = models.IntegerField(default=0)
    decision = models.CharField(
        max_length=10,
        choices=Decision.choices(),
        default=Decision.DECLINE.value
    )

    class Meta:
        unique_together = ('user', 'queue')
