# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Task, Category, ActivityLog

@receiver(post_save, sender=Task)
def log_task_activity(sender, instance, created, **kwargs):
    if created:
        action = 'task_add'
        details = f"Task '{instance.title}' added."
    else:
        if instance.completed:
            action = 'task_complete'
            details = f"Task '{instance.title}' completed."
        else:
            action = 'task_update'
            details = f"Task '{instance.title}' updated."

    ActivityLog.objects.create(
        user=instance.user,
        action=action,
        object_id=instance.id,
        details=details
    )

@receiver(post_delete, sender=Task)
def log_task_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action='task_delete',
        object_id=instance.id,
        details=f"Task '{instance.title}' deleted."
    )

@receiver(post_save, sender=Category)
def log_category_activity(sender, instance, created, **kwargs):
    action = 'category_add' if created else 'category_update'
    ActivityLog.objects.create(
        user=instance.user,
        action=action,
        object_id=instance.id,
        details=f"Category '{instance.name}' {'created' if created else 'updated'}."
    )

@receiver(post_delete, sender=Category)
def log_category_delete(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action='category_delete',
        object_id=instance.id,
        details=f"Category '{instance.name}' deleted."
    )
