# Generated by Django 5.0.7 on 2024-07-21 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0011_task_reccuring_task_recurring_interval'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='reccuring',
            new_name='recurring',
        ),
    ]
