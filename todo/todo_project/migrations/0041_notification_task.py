# Generated by Django 5.1.1 on 2024-09-10 10:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0040_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='todo_project.task'),
        ),
    ]
