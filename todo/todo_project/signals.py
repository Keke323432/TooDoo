# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Task, Category, ActivityLog, Notification, User
from django.urls import reverse

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


@receiver(post_save, sender=Task)
def log_task_assignment(sender, instance, created, **kwargs):
    if created:
        # Task is newly created, notify the user if assigned immediately
        if instance.assigned_to:
            message = f"You have been assigned to: {instance.title}"
            Notification.objects.create(user=instance.assigned_to, message=message, task=instance)

    else:
        # If the task already exists, check if assigned_to has changed
        previous = Task.objects.get(pk=instance.pk)
        if previous.assigned_to != instance.assigned_to:
            if previous.assigned_to:
                # Notify the previous assignee that they are no longer assigned
                message = f"You have been unassigned from: '{instance.title}'"
                Notification.objects.create(user=previous.assigned_to, message=message, task=instance)
                
            if instance.assigned_to:
                # Notify the new assignee that they have been assigned the task
                message = f"You have been assigned to: '{instance.title}'"
                Notification.objects.create(user=instance.assigned_to, message=message, task=instance)