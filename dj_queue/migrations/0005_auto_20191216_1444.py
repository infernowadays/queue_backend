# Generated by Django 2.2.7 on 2019-12-16 14:44

import dj_queue.enums
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dj_queue', '0004_invitations'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.CharField(choices=[('ACCEPT', 'ACCEPT'), ('DECLINE', 'DECLINE')], default=dj_queue.enums.Decision('DECLINE'), max_length=10)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('queue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dj_queue.Queue')),
            ],
            options={
                'unique_together': {('queue', 'member')},
            },
        ),
        migrations.DeleteModel(
            name='Invitations',
        ),
    ]
