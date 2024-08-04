from django.views.generic.base import ContextMixin
# class based views imported from django.generic
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView
from .models import Task, Category, Comment
# only logged in users can access this view
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import EditForm, CreateForm,CommentForm,AddCategoryForm
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse


class TaskCountsMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['all_tasks_count'] = Task.objects.filter(user=user, completed = False).count()
        context['scheduled_tasks_count'] = Task.objects.filter(user=user, due_date__gte=timezone.now(), completed=False).count()
        context['overdue_tasks_count'] = Task.objects.filter(user=user, due_date__lt=timezone.now(), completed=False).count()
        context['completed_tasks_count'] = Task.objects.filter(user=user, completed=True).count()
        context['low_tasks_count'] = Task.objects.filter(user=user, priority='low' ,completed=False).count()
        context['medium_tasks_count'] = Task.objects.filter(user=user, priority='medium' ,completed=False).count()
        context['high_tasks_count'] = Task.objects.filter(user=user, priority='high' ,completed=False).count()
        context['urgent_tasks_count'] = Task.objects.filter(user=user, priority='urgent' ,completed=False).count()
        return context

class TaskListView(LoginRequiredMixin, TaskCountsMixin, ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
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
        return Task.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['category'].queryset = Category.objects.filter(
            user=self.request.user)
        return form


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'delete_task.html'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


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
    context_object_name = 'cats'  # Renamed to better reflect the data

    def get_queryset(self):
        # Get the category ID from URL parameters
        category_id = self.kwargs.get('category_id')

        # Fetch the tasks for the given category and ensure they belong to the logged-in user
        return Task.objects.filter(category_id=category_id, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')

        # Get the category object and ensure it belongs to the logged-in user
        category = get_object_or_404(
            Category, id=category_id, user=self.request.user)

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
        queryset = Task.objects.filter(user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context


class CompletedTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'completed_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user, completed=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_count'] = self.get_queryset().count()
        return context


class ScheduledTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'scheduled_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()
        queryset = Task.objects.filter(user=user,  due_date__gte=now, due_date__isnull=False)
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
            comment.post = task  # Use 'post' to match the model. Retrieve the related comment from the task
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
        
class DeleteCommentView(LoginRequiredMixin,DeleteView):
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
        queryset = Task.objects.filter(user=user)
        return queryset
    

class BookmarkView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'bookmark_list.html'
    context_object_name = 'tasks'  # this can be used in the template to get the objects

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user, bookmarked=True)
        return queryset

