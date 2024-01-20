# Generated by Django 4.2.6 on 2024-01-20 15:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0010_alter_course_course_initials'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='timetable',
        ),
        migrations.AddField(
            model_name='course',
            name='timetable',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='timetable.timetable'),
            preserve_default=False,
        ),
    ]
