# Generated by Django 4.2.6 on 2023-12-31 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0005_course_course_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timetable',
            name='timetable_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]