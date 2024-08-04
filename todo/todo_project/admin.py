from django.contrib import admin
from .models import Task,Category,Comment,Profile

admin.site.register(Task)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Profile)
