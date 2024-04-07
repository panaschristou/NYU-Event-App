import datetime
from django.db import models
from django.contrib.auth.models import User

from backend.storage import OverwriteStorage


def profile_avatar_name(instance, filename):
    ext = filename.split(".")[-1]
    return "profile_images/%s.%s" % (instance.user.username, ext)


# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        storage=OverwriteStorage(), upload_to=profile_avatar_name, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username


# Event model
class Event(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=1000, default="Category not defined")
    description = models.TextField(blank=True)
    open_date = models.DateField(default=datetime.date.today)
    close_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=1000)
    external_link = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    avg_rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title


# Review model
class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name="liked_reviews", blank=True)
    reply_count = models.IntegerField(default=0)


class ReplyToReview(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    fromUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="replies_from"
    )
    toUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="replies_to"
    )
    reply_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reply_text


# UserEvent model for likes/saves
class UserEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saved = models.BooleanField(default=False)


# Chat model
class Chat(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_chats"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_chats"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


# Group Chat model
class Room3(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)


class ChatRoom3(models.Model):
    sender_ChatRoom = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_chats_room"
    )
    receiver_room_slug = models.TextField()
    # receiver_room_slug = models.ForeignKey(Room, related_name="received_chats_room", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class user_rooms(models.Model):
    user_detail = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_detail"
    )
    room_joined = models.ForeignKey(
        Room3, on_delete=models.CASCADE, related_name="room_joined"
    )


# Search History Model
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    search_type = models.CharField(max_length=10)


class SuspendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reason = models.TextField()
    suspended_at = models.DateTimeField(auto_now_add=True)
    unsuspended_at = models.DateTimeField(null=True, blank=True)
    is_suspended = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def unsuspend_user(self):
        self.is_suspended = False
        self.user.save()
        self.delete()


class BannedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reason = models.TextField()
    banned_at = models.DateTimeField(auto_now_add=True)
    unban_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def unban_user(self):
        self.user.is_active = True
        self.user.save()
        self.delete()
