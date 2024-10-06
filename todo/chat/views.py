from django.shortcuts import render, redirect, get_object_or_404
from todo_project.models import Message, Conversation
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def chatPage(request, *args, **kwargs):
    print("Chat page view called")  # Debugging
    if not request.user.is_authenticated:
        return redirect("login-user")

    # Fetch previous messages from the database
    messages = Message.objects.filter(
        room_name="group_chat_gfg").order_by('timestamp')
    print(messages)  # Debugging

    context = {
        'messages': messages
    }
    return render(request, "chat/chatpage.html", context)

@login_required
def private_chat_page(request, conversation_id):
    
    # Fetch the conversation and its messages
    conversation = Conversation.objects.get(id=conversation_id)
    messages = conversation.messages.all().order_by('timestamp')

    context = {
        'conversation': conversation,
        'messages': messages
    }
    
    return render(request, "chat/private_chat.html", context)


def start_chat(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login-user')

    other_user = get_object_or_404(User, id=user_id)

    # Get the conversation between the two users
    conversation = Conversation.objects.filter(
        participants=other_user).filter(participants=request.user).first()

    # If no conversation exists, create a new one
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    # Redirect to the private chat page with the conversation ID
    return redirect('private-chat-page', conversation_id=conversation.id)


def inbox(request):
    # Retrieve all conversations that involve the logged-in user
    conversations = Conversation.objects.filter(participants=request.user)

    return render(request, 'chat/inbox.html', {
        'conversations': conversations,
    })



@login_required
def delete_chat(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)

    # Ensure the user is a participant in the conversation
    if request.user in conversation.participants.all():
        conversation.delete()
        return redirect('inbox')
    else:
        return HttpResponseForbidden("You are not allowed to delete this conversation.")
