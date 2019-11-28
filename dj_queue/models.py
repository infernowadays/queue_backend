from django.db import models, transaction
from django.contrib.auth.models import User


class Queue(models.Model):
    name = models.TextField(default='')
    owner = models.ForeignKey(User, null=True, db_constraint=False, on_delete=models.SET_NULL)
    members = models.ManyToManyField(User, related_name='queues', through='Membership')


class Membership(models.Model):
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.IntegerField(default=-1)

    class Meta:
        unique_together = ('queue', 'member',)
