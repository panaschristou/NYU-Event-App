from django.db import models
from django.contrib.auth.models import User

# Event model
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    nyu_discount_url = models.URLField()
    image_url = models.URLField(null=True, blank=True)  

# Review model
class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# UserEvent model for likes/saves
class UserEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)

# Chat model
class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

