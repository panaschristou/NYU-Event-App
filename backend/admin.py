# admin.py

from django.contrib import admin
from .models import Event, Review, UserEvent, Chat, Profile

admin.site.register(Event)
admin.site.register(Review)
admin.site.register(UserEvent)
admin.site.register(Chat)
admin.site.register(Profile)
