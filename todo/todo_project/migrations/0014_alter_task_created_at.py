# Generated by Django 5.0.7 on 2024-07-25 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0013_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='created_at',
            field=models.DateField(auto_now_add=True),
        ),
    ]
