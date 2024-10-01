from django.urls import path , include
from chat.consumers import ChatConsumer, PrivateChatConsumer

# Here, "" is routing to the URL ChatConsumer which 
# will handle the chat functionality.
websocket_urlpatterns = [
    path("" , ChatConsumer.as_asgi()) , 
    path('private/<int:conversation_id>/', PrivateChatConsumer.as_asgi()),
] 
