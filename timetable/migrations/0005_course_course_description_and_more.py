# Generated by Django 4.2.6 on 2023-12-31 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0004_activity_teacher_alter_teacher_teacher_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_description',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='activity_type',
            name='type_color',
            field=models.CharField(default='#D7D3BA', max_length=10),
        ),
        migrations.AlterField(
            model_name='activity_type',
            name='type_name',
            field=models.CharField(blank=True, default=models.CharField(default='def', max_length=100), max_length=100),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='teacher_initials',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
