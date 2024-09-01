from django.contrib import admin
from .models import Task,Category,Comment,Profile,Message,Conversation,ActivityLog

admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(ActivityLog)