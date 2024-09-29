from django.shortcuts import render, redirect
from todo_project.models import Message


def chatPage(request, *args, **kwargs):
    print("Chat page view called")  # Debugging
    if not request.user.is_authenticated:
        return redirect("login-user")

    # Fetch previous messages from the database
    messages = Message.objects.filter(room_name="group_chat_gfg").order_by('timestamp')
    print(messages)  # Debugging

    context = {
        'messages': messages
    }
    return render(request, "chat/chatpage.html", context)