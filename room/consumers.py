import json
import logging

from django.contrib.auth.models import User
from room.channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Room, Message

from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = "chat_%s" % self.room_name

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()

            logger.info(f"Client connected to room {self.room_name}")
        except Exception as e:
            logger.error(f"Error connecting client: {e}")

    async def disconnect(self):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

            logger.info(f"Client disconnected from room {self.room_name}")
        except Exception as e:
            logger.error(f"Error disconnecting client: {e}")

        # Receive message from WebSocket

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message = data["message"]
        username = data["username"]
        room = data["room"]

        await self.save_message(username, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
                "room": room,
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        room = event["room"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "room": room,
                }
            )
        )

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)

        Message.objects.create(user=user, room=room, content=message)
