from django.views.generic.base import ContextMixin
# class based views imported from django.generic
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView
from .models import Task, Category, Comment
# only logged in users can access this view
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import EditForm, CreateForm, CommentForm, AddCategoryForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, ActivityLog, Notification
from .forms import MessageForm
from django.db.models import Q, Count
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
            Q(user=user) | Q(assigned_to=user),
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
        dates = [start_date + timedelta(days=i) for i in range(8)]  # 8 to include end_date
        priority_data = {priority: [0] * len(dates) for priority in ['low', 'medium', 'high', 'urgent']}

        # Count tasks per day
        for priority in priority_data.keys():
            for i, date in enumerate(dates):
                start_of_day = datetime.combine(date, datetime.min.time())
                end_of_day = start_of_day + timedelta(days=1)  # End of the day is 24 hours from start_of_day
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
        context['dates'] = [date.strftime('%Y-%m-%dT%H:%M:%S.%fZ') for date in dates]  

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
        # Include tasks for both the creator and the assignee
        return Task.objects.filter(
            Q(user=self.request.user) | Q(assigned_to=self.request.user)
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(
            Q(user=self.request.user) | Q(user__in=User.objects.filter(
                task__assigned_to=self.request.user))
        ).distinct()
        return form

    def form_valid(self, form):
        task = form.instance
        
        # If the task is a clone (i.e., it has an parent task)
        if task.parent_task:
            # If "recurring" is unchecked on the clone
            if not form.cleaned_data['recurring']:
                # Find the parent task and set its "recurring" field to False
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
    context_object_name = 'tasks'  # This can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        # Include tasks created by the user or assigned to the user
        queryset = Task.objects.filter(Q(user=user) | Q(assigned_to=user))
        return queryset


class CompletedTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'completed_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        # Filter tasks to only include completed ones
        return Task.objects.filter(completed=True, user=self.request.user)

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


class BookmarkView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'bookmark_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user, bookmarked=True)
        return queryset


def inbox(request):
    # Retrieve all conversations that involve the logged-in user
    conversations = Conversation.objects.filter(participants=request.user)

    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
    })


@login_required
def send_message(request, username):
    recipient = get_object_or_404(User, username=username)

    # Get the conversation that includes exactly both the logged-in user and the recipient
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=recipient
    ).distinct()  # Ensure we only get unique conversations

    # There should be only one conversation that includes both users
    if conversation.exists():
        conversation = conversation.first()
    else:
        # Create a new conversation if none exists
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
        conversation.save()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()
            return redirect('message_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    return render(request, 'messaging/send_message.html', {
        'form': form,
        'recipient': recipient,
    })


@login_required
def message_detail(request, conversation_id):
    # Retrieve the conversation based on the ID
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Ensure that the logged-in user is a participant in the conversation
    if request.user not in conversation.participants.all():
        # Redirect to inbox if user is not a participant
        return redirect('inbox')

    messages = conversation.messages.order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()
            return redirect('message_detail', conversation_id=conversation_id)
    else:
        form = MessageForm()

    return render(request, 'messaging/message_detail.html', {
        'messages': messages,
        'conversation': conversation,
        'form': form,
    })


class DeleteMessageView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Conversation
    template_name = 'messaging/delete_message.html'
    success_url = reverse_lazy('inbox')  # Redirect to inbox after deletion

    def get_object(self, queryset=None):
        # Get the conversation object based on the URL parameter
        return Conversation.objects.get(pk=self.kwargs.get('conversation_id'))

    def test_func(self):
        """Ensure that only participants of the conversation can delete it."""
        conversation = self.get_object()
        return self.request.user in conversation.participants.all()


class RecentActivityView(ListView):
    model = ActivityLog
    template_name = 'recent_activity.html'
    context_object_name = 'activities'
    # Adjust ordering based on your model's timestamp field
    ordering = ['-timestamp']




def notifications_view(request):
    if request.user.is_authenticated:
        notifications_unread = Notification.objects.filter(user=request.user, is_read=False)
        notifications_read = Notification.objects.filter(user=request.user, is_read=True)
        return render(request, 'notifications.html', {
            'notifications_unread': notifications_unread,
            'notifications_read': notifications_read,
        })
    return redirect('login')  # Adjust redirect if needed
    


def mark_notifications_as_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
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
            context['notificationss_unread'] = Notification.objects.filter(user=self.request.user, is_read=False).order_by('-timestamp')
            context['notificationss_read'] = Notification.objects.filter(user=self.request.user, is_read=True).order_by('-timestamp')
        else:
            context['notificationss_unread'] = []
            context['notificationss_read'] = []
        return context