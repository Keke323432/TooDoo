from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class Category(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, blank=True, default='#FFFFFF')  
    def __str__(self):
        return self.name + ''

def one_week_hence():
    return datetime.now() + timedelta(weeks=1)




class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # on_delete=models.Cascade - When delete the post delete the associated user too from the database
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(blank=True, null=True)
    recurring = models.BooleanField(default=False)
    recurring_end_date = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='static/img/', blank=True, null=True)
    bookmarked = models.BooleanField(default=False)
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, null=True)
    
    RECURRING_CHOICES = [
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
    post = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE) # on_delete=models.Cascade - When delete the post delete all the comments too
    name = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)
    
    
