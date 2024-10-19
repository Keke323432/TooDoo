from django.views.generic.base import ContextMixin
# class based views imported from django.generic
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView
from .models import Task, Category, Comment, Conversation, ActivityLog, Notification, UserCategory
# only logged in users can access this view
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import EditForm, CreateForm, CommentForm, AddCategoryForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import timedelta, datetime


class TaskCountsMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        start_date = today - timedelta(days=7)

        # Current counts for pie chart
        context['all_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            completed=False
        ).count()
        context['recurring_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            recurring=True,
            completed=False
        ).count()
        context['scheduled_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            due_date__gte=timezone.now(),
            completed=False
        ).count()
        context['overdue_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            due_date__lt=timezone.now(),
            completed=False
        ).count()
        context['completed_tasks_count'] = Task.objects.filter(
            completed=True
        ).count()
        context['low_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            priority='low',
            completed=False
        ).count()
        context['medium_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            priority='medium',
            completed=False
        ).count()
        context['high_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            priority='high',
            completed=False
        ).count()
        context['urgent_tasks_count'] = Task.objects.filter(
            Q(user=user) | Q(assigned_to=user),
            priority='urgent',
            completed=False
        ).count()

        # Data for the line chart
        dates = [start_date + timedelta(days=i)
                 for i in range(8)]  # 8 to include end_date
        priority_data = {priority: [
            0] * len(dates) for priority in ['low', 'medium', 'high', 'urgent']}

        # Count tasks per day
        for priority in priority_data.keys():
            for i, date in enumerate(dates):
                start_of_day = datetime.combine(date, datetime.min.time())
                # End of the day is 24 hours from start_of_day
                end_of_day = start_of_day + timedelta(days=1)
                count = Task.objects.filter(
                    Q(user=user) | Q(assigned_to=user),
                    priority=priority,
                    created_at__gte=start_of_day,
                    created_at__lt=end_of_day  # Use < for exclusive end
                ).count()
                priority_data[priority][i] = count

        context['low_priority'] = priority_data['low']
        context['medium_priority'] = priority_data['medium']
        context['high_priority'] = priority_data['high']
        context['urgent_priority'] = priority_data['urgent']
        context['dates'] = [date.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ') for date in dates]

        return context


class TaskListView(LoginRequiredMixin, TaskCountsMixin, ListView):
    model = Task
    template_name = 'task_list.html'  # aka home. too lazy to change names
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['recent_activities'] = ActivityLog.objects.filter(
            user=self.request.user,
            timestamp__gte=timezone.now() - timedelta(hours=1)
        ).order_by('-timestamp')[:15]

        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'create_task.html'
    form_class = CreateForm
    success_url = reverse_lazy('task_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the logged-in user to the form
        kwargs['user'] = self.request.user
        return kwargs

    # Associates the current logged-in user with the newly created task.
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'update_task.html'
    form_class = EditForm
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        # Return all tasks without any restrictions on user
        return Task.objects.all()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Remove restrictions on categories so all categories are visible
        form.fields['category'].queryset = Category.objects.all()
        return form

    def form_valid(self, form):
        task = form.instance

        # Handle recurring tasks if necessary
        if task.parent_task:
            if not form.cleaned_data['recurring']:
                parent_task = task.parent_task
                parent_task.recurring = False
                parent_task.save()

        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'delete_task.html'
    # Redirect to the list of tasks after deletion
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        user = self.request.user
        # Allow access if the user is the creator or is assigned to the task
        return Task.objects.filter(Q(user=user) | Q(assigned_to=user))


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all()  # Fetch all categories

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch UserCategory objects for the current user
        user_categories = UserCategory.objects.filter(user=self.request.user).values_list('category_id', flat=True)
        # Pass the IDs of categories added to the sidebar by the user
        context['user_categories'] = user_categories
        return context


class AddCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = AddCategoryForm
    template_name = 'add_category.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskByCategoryView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks_by_category.html'
    context_object_name = 'cats'

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        # Fetch tasks for the given category; no user restriction
        return Task.objects.filter(category_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')

        # Get the category object; no user restriction
        category = get_object_or_404(Category, id=category_id)

        context['category'] = category
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'delete_category.html'
    success_url = reverse_lazy('category_list')


class AllTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'all_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        # Fetch all tasks created by the user or assigned to the user
        queryset = Task.objects.filter(Q(user=user) | Q(assigned_to=user)).select_related('category')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get categories that have tasks created by or assigned to the user
        categories_with_tasks = Category.objects.filter(
            task__in=Task.objects.filter(Q(user=user) | Q(assigned_to=user))
        ).distinct()

        # Pass tasks grouped by categories, including uncategorized
        context['tasks'] = self.get_queryset()
        context['categories'] = categories_with_tasks

        return context


class CompletedTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'completed_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        # Filter tasks to only include completed ones
        return Task.objects.filter(completed=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Count only completed tasks
        context['task_completed_count'] = self.get_queryset().count()
        return context


class ScheduledTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'scheduled_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        queryset = Task.objects.filter(
            user=user,  due_date__gte=now, due_date__isnull=False)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get categories that have tasks created by or assigned to the user
        categories_with_tasks = Category.objects.filter(
            task__in=Task.objects.filter(Q(user=user) | Q(assigned_to=user))
        ).distinct()

        # Pass tasks grouped by categories, including uncategorized
        context['tasks'] = self.get_queryset()
        context['categories'] = categories_with_tasks

        return context


class OverdueTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'overdue_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        # __lt stands for "less than". This condition filters tasks where the due_date is less than the current date and time, meaning the tasks are overdue.
        queryset = Task.objects.filter(
            user=user, due_date__lt=now, due_date__isnull=False)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get categories that have tasks created by or assigned to the user
        categories_with_tasks = Category.objects.filter(
            task__in=Task.objects.filter(Q(user=user) | Q(assigned_to=user))
        ).distinct()

        # Pass tasks grouped by categories, including uncategorized
        context['tasks'] = self.get_queryset()
        context['categories'] = categories_with_tasks

        return context


class SearchTaskView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'search_task.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Task.objects.filter(user=self.request.user, title__icontains=query)
        else:
            return Task.objects.none()


def mark_completed(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        task_id = data.get('task_id')
        completed = data.get('completed')

        try:
            task = Task.objects.get(id=task_id)
            task.completed = completed
            task.save()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


class ClearCompletedTasksView(RedirectView):
    # Redirect to the completed list after deletion
    url = reverse_lazy('completed_list')

    def post(self, request, *args, **kwargs):
        # Delete all completed tasks
        Task.objects.filter(completed=True).delete()
        return super().post(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            task = get_object_or_404(Task, id=self.kwargs['task_id'])
            # Use 'post' to match the model. Retrieve the related comment from the task
            comment.post = task
            comment.user = request.user  # Set the current user
            comment.save()
            # redirects to the same task by taking the id kwargs and shit
            return redirect(reverse_lazy('update_task', kwargs={'pk': task.id}))
        else:
            return self.form_invalid(form)


class EditCommentView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'edit_comment.html'

    def form_valid(self, form):
        comment = form.save(commit=False)
        task = comment.post  # Retrieve the related task from the comment
        comment.save()
        return redirect(reverse_lazy('update_task', kwargs={'pk': task.id}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'delete_comment.html'
    # Since the success URL needs to include the pk of the related task, it cannot be determined statically when defining the class. Instead, it must be calculated based on the specific instance of the comment that is being deleted.

    def get_success_url(self):
        comment = self.object
        task = comment.post
        return reverse_lazy('update_task', kwargs={'pk': task.pk})


class RecurringListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'recurring_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()  # Get today's date
        queryset = Task.objects.filter(
            user=user,
            recurring=True,  # Only include tasks marked as recurring
            completed=False,
        )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get categories that have tasks created by or assigned to the user
        categories_with_tasks = Category.objects.filter(
            task__in=Task.objects.filter(Q(user=user) | Q(assigned_to=user))
        ).distinct()

        # Pass tasks grouped by categories, including uncategorized
        context['tasks'] = self.get_queryset()
        context['categories'] = categories_with_tasks

        return context


class BookmarkView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'bookmark_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user, bookmarked=True)
        return queryset



class RecentActivityView(ListView):
    model = ActivityLog
    template_name = 'recent_activity.html'
    context_object_name = 'activities'
    # Adjust ordering based on your model's timestamp field
    ordering = ['-timestamp']


def notifications_view(request):
    if request.user.is_authenticated:
        notifications_unread = Notification.objects.filter(
            user=request.user, is_read=False)
        notifications_read = Notification.objects.filter(
            user=request.user, is_read=True)
        return render(request, 'notifications.html', {
            'notifications_unread': notifications_unread,
            'notifications_read': notifications_read,
        })
    return redirect('login')  # Adjust redirect if needed


def mark_notifications_as_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(
            user=request.user, is_read=False).update(is_read=True)
    return redirect('task_list')


class NotificationsView(ListView):
    model = Notification
    template_name = 'notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        """
        Return all notifications for the authenticated user.
        """
        if self.request.user.is_authenticated:
            return Notification.objects.filter(user=self.request.user)
        return Notification.objects.none()

    def get_context_data(self, **kwargs):
        """
        Add additional context for unread and read notifications.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['notificationss_unread'] = Notification.objects.filter(
                user=self.request.user, is_read=False).order_by('-timestamp')
            context['notificationss_read'] = Notification.objects.filter(
                user=self.request.user, is_read=True).order_by('-timestamp')
        else:
            context['notificationss_unread'] = []
            context['notificationss_read'] = []
        return context


@login_required
def mark_global(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    UserCategory.objects.get_or_create(user=request.user, category=category)  # Add category to user's sidebar
    return redirect('category_list')  # Redirect to category list or any other page

@login_required
def unmark_global(request, category_id):
    user_category = get_object_or_404(UserCategory, user=request.user, category_id=category_id)
    user_category.delete()  # Remove category from user's sidebar
    return redirect('category_list')  # Redirect to category list or any other page