# Generated by Django 4.2.6 on 2024-01-01 17:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0006_alter_timetable_timetable_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='share_link',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
