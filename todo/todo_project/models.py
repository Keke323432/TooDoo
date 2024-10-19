from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, blank=True, default='#FFFFFF')  
    is_global = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ''

class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'category')  # Ensure each user can only add a category once


def one_week_hence():
    return datetime.now() + timedelta(weeks=1)




class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # on_delete=models.Cascade - When delete the post delete the associated user too from the database
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, related_name='assigned_tasks', blank=True, null=True, on_delete=models.CASCADE)  # Change to ForeignKeyo
    completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(blank=True, null=True)
    recurring = models.BooleanField(default=False)
    recurring_start_date = models.DateField(blank=True, null=True)  # New field
    recurring_end_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='static/img/', blank=True, null=True)
    bookmarked = models.BooleanField(default=False)
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='clones')
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, null=True)
    
    RECURRING_CHOICES = [
        ('minute', 'Every Minute'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    recurring_interval = models.CharField(max_length=10, choices=RECURRING_CHOICES, blank=True, null=True)

    
    def __str__(self):
        return self.title + ''

class Profile(models.Model):
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_images/', default='profile_images/default-profile-pic.png')
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    x_profile = models.CharField(max_length=100, blank=True, null=True)
    instagram_profile = models.CharField(max_length=100, blank=True, null=True)
    linkedin_profile = models.CharField(max_length=100, blank=True, null=True)
    facebook_profile = models.CharField(max_length=100, blank=True, null=True)
    
    
    
    def __str__(self):
        return f"{self.user.username}'s Profile" if self.user else 'Profile without user'

class Comment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)  # Changed to ForeignKey
    post = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE) # on_delete=models.Cascade - When delete the post delete all the comments too
    name = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)
    
    

class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {', '.join([user.username for user in self.participants.all()])}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    room_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
    
class PrivateMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content} at {self.timestamp}"
    
    
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('task_add', 'Added Task'),
        ('task_update', 'Updated Task'),
        ('task_delete', 'Deleted Task'),
        ('category_add', 'Created Category'),
        ('category_delete', 'Deleted Category'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_id = models.IntegerField()  # ID of the related object
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)  # Optional details

    def __str__(self):
        return f"{self.user} {self.get_action_display()} at {self.timestamp}"
    
    
    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User receiving the notification
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)  # To track if the notification is read
    timestamp = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)  # Optional field for task

    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"