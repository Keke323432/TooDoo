# Generated by Django 5.0.7 on 2024-07-26 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo_project', '0015_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='color',
            field=models.CharField(blank=True, default='#FFFFFF', max_length=7),
        ),
    ]
