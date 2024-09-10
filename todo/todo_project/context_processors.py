from .models import Profile, Category,Conversation,Notification
from django.db.models import Max




def profile_context(request):              # this pulls the template globally. Context processors are good to be used when you want to pull info to all templates. :d 
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        return {'profile': profile}
    return {}



def category_list(request):
    if request.user.is_authenticated:
        categories = Category.objects.all()
    else:
        categories = Category.objects.none()  # No categories for unauthenticated users
    return {'categories': categories}


def latest_conversations(request):
    if request.user.is_authenticated:
        # Retrieve conversations for the logged-in user
        conversations = Conversation.objects.filter(participants=request.user)
        return {
            'latest_conversations': conversations
        }
    return {}


def get_notifications(request):
    if request.user.is_authenticated:
        notifications_unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')[:5]
        notifications_read = Notification.objects.filter(user=request.user, is_read=True).order_by('-timestamp')[:5]
        return {
            'notifications_unread': notifications_unread,
            'notifications_read': notifications_read,
        }
    return {
        'notifications_unread': [],
        'notifications_read': [],
    }