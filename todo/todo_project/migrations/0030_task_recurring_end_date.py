# Generated by Django 5.0.7 on 2024-08-01 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0029_task_bookmarked'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='recurring_end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
