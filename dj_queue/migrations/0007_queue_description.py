# Generated by Django 2.2.7 on 2019-12-16 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dj_queue', '0006_auto_20191216_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
