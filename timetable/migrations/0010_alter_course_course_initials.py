# Generated by Django 4.2.6 on 2024-01-17 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0009_alter_activity_type_type_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_initials',
            field=models.CharField(max_length=30),
        ),
    ]