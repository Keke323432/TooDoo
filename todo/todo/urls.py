
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('todo_project.urls')),
    path('members/',include('django.contrib.auth.urls')),
    path('members/',include('members.urls')),
    path("chat/", include("chat.urls")),
]
