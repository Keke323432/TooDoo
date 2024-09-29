from django.urls import path
from .views import TaskCreateView, TaskUpdateView, TaskDeleteView,TaskListView,CategoryListView,AddCategoryView,TaskByCategoryView,CategoryDeleteView,AllTaskListView, CompletedTaskListView,ScheduledTaskListView, OverdueTaskListView,SearchTaskView,mark_completed,ClearCompletedTasksView,AddCommentView,EditCommentView,DeleteCommentView,RecurringListView,BookmarkView,RecentActivityView,mark_notifications_as_read,NotificationsView,mark_category_global,unmark_category_global
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    
    path('', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='create_task'),
    path('update/<int:pk>/', TaskUpdateView.as_view(), name='update_task'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='delete_task'),
    path('category_list/', CategoryListView.as_view(), name='category_list'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('tasks/<int:category_id>/', TaskByCategoryView.as_view(), name='tasks_by_category'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='delete_category'),
    path('all_list', AllTaskListView.as_view(), name='all_list'),
    path('completed_list/', CompletedTaskListView.as_view(), name='completed_list'),
    path('scheduled_list/', ScheduledTaskListView.as_view(), name='scheduled_list'),
    path('overdue_list/', OverdueTaskListView.as_view(), name='overdue_list'),
    path('search_task/', SearchTaskView.as_view(), name='search_task'),
    path('mark_completed/', mark_completed, name='mark_completed'),
    path('clear_completed/', ClearCompletedTasksView.as_view(), name='clear_completed'),
    path('add_comment/<int:task_id>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('edit_comment/<int:pk>/comment/', EditCommentView.as_view(), name='edit_comment'),
    path('delete_comment/<int:pk>/comment/', DeleteCommentView.as_view(), name='delete_comment'),
    path('recurring_list/', RecurringListView.as_view(), name='recurring_list'),
    path('bookmark_list/', BookmarkView.as_view(), name='bookmark_list'),
    path('inbox/', views.inbox, name='inbox'),
    path('recent_activity/', RecentActivityView.as_view(), name='recent_activity'),
    path('mark-as-read/', mark_notifications_as_read, name='mark_notifications_as_read'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('categories/mark_global/<int:category_id>/', mark_category_global, name='mark_global'),
    path('categories/unmark_global/<int:category_id>/', unmark_category_global, name='unmark_global'),
    

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

