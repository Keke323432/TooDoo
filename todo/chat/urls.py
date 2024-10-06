from django.urls import path
from chat import views as chat_views
from .views import private_chat_page, start_chat, inbox,delete_chat


urlpatterns = [
    path("chat_home/", chat_views.chatPage, name="chatpage"),
    path('private-chat/<int:conversation_id>/', private_chat_page, name='private-chat-page'),
    path('start-chat/<int:user_id>/', start_chat, name='start-chat'),
    path('inbox/', inbox, name='inbox'),
    path('chat/delete_chat/<int:pk>/', delete_chat, name='delete_chat'),
    
]
