from .models import Profile, Category,Conversation,Notification, UserCategory
from django.db.models import Max
from django.db.models import Q




def profile_context(request):              # this pulls the template globally. Context processors are good to be used when you want to pull info to all templates. :d 
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        return {'profile': profile}
    return {}


def sidebar_categories(request):
    if request.user.is_authenticated:
        # Fetch only categories marked by the user for their sidebar
        categories = UserCategory.objects.filter(user=request.user).select_related('category')
        return {'categoriess': [user_category.category for user_category in categories]}
    else:
        return {'categoriess': []}  # No categories for unauthenticated users




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
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'notifications_unread': notifications_unread,
            'notifications_read': notifications_read,
            'unread_count': unread_count,
        }
    return {
        'notifications_unread': [],
        'notifications_read': [],
        'unread_count': 0,
    }