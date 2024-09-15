from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from todo_project.models import Task
from django.utils import timezone

class Command(BaseCommand):
    help = "Check and create recurring tasks."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()  # Use timezone-aware now
        tasks = Task.objects.filter(
            recurring=True,
            recurring_end_date__gte=today
        )

        for task in tasks:
            if not task.due_date:
                continue  # Skip tasks where due_date is not set

            if task.recurring_interval == 'minute':
                next_due_date = task.due_date + timedelta(minutes=1)
            elif task.recurring_interval == 'daily':
                next_due_date = task.due_date + timedelta(days=1)
            elif task.recurring_interval == 'weekly':
                next_due_date = task.due_date + timedelta(weeks=1)
            elif task.recurring_interval == 'monthly':
                next_due_date = task.due_date + timedelta(days=30)  # Approximate one month

            if next_due_date and task.recurring_start_date <= next_due_date <= task.recurring_end_date:
                Task.objects.create(
                user=task.user,
                title=task.title,
                description=task.description,
                assigned_to=task.assigned_to,
                due_date=next_due_date,
                category=task.category,
                recurring=True,  # Clones are not recurring
                priority=task.priority,
                file=task.file,
                bookmarked=task.bookmarked,
                parent_task=task  # Set the original task reference
            )

        self.stdout.write(self.style.SUCCESS('Recurring tasks checked and updated.'))
