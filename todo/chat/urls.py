from django.urls import path
from chat import views as chat_views


urlpatterns = [
    path("chat_home/", chat_views.chatPage, name="chatpage"),
]
