# Generated by Django 5.0.7 on 2024-07-20 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0009_alter_task_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
