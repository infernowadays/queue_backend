from django.db import models
from django.contrib.auth.models import User


class Queue(models.Model):
    user = models.ManyToManyField(User)
    distribution = models.CharField(max_length=30)
