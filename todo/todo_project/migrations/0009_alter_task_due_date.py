# Generated by Django 5.0.7 on 2024-07-20 18:04

import todo_project.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0008_alter_task_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True, default=todo_project.models.one_week_hence, null=True),
        ),
    ]
