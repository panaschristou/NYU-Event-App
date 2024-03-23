from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
]


# from django.urls import re_path

# websocket_urlpatterns = [
#     re_path(r'^ws/work/$', consumers.ChatConsumer.as_asgi()),
# ]
