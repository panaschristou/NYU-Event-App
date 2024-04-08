from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from backend.models import Chat, ChatRoom3
from backend.views.pusher_config import pusher_client
from django.contrib.auth.models import User
from ..models import Room3, user_rooms
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.views.decorators.http import require_POST


@login_required
def group_chat_index(request):

    current_user = request.user

    user_room_objects = user_rooms.objects.filter(user_detail=current_user)
    print("rooms = ", user_room_objects)

    return render(request, "group_chat_index.html", {"rooms": user_room_objects})


def search_rooms(request):
    if "query" in request.GET:
        query = request.GET["query"]
        rooms = Room3.objects.filter(slug__icontains=query)
        return render(request, "partials/user_search_results.html", {"users": rooms})
    else:
        return JsonResponse({"error": "No search term provided"}, status=400)


@login_required
def chat_with_room(request, receiver_room_slug):
    room = get_object_or_404(Room3, slug=receiver_room_slug)

    current_user = request.user

    current_room = Room3.objects.get(slug=receiver_room_slug)

    try:
        user_rooms.objects.get(user_detail=current_user, room_joined=current_room)
    except user_rooms.DoesNotExist:
        user_rooms.objects.create(user_detail=current_user, room_joined=current_room)

    chat_messages = ChatRoom3.objects.filter(
        # Q(sender_ChatRoom=request.user, receiver_room_slug=receiver_room_slug)
        Q(receiver_room_slug=receiver_room_slug)
        # | Q(sender_id=receiver_room_slug, receiver=request.user)
    ).order_by("timestamp")

    return render(
        request,
        "group_chat_with_user.html",
        {
            "user_id": request.user.id,
            "room": room,
            "chat_messages": chat_messages,
        },
    )


@login_required
@require_POST
def send_message(request, receiver_room_slug):
    sender = request.user
    # receiver = request.POST.get('receiver_id')
    message = request.POST.get("message")
    receiver_room = Room3.objects.get(slug=receiver_room_slug)
    # save the message to the database
    ChatRoom3.objects.create(
        sender_ChatRoom=sender, receiver_room_slug=receiver_room.slug, message=message
    )

    # Trigger a Pusher event
    channel_name = get_chat_channel_name(request.user.id, receiver_room.slug)
    pusher_client.trigger(
        channel_name,
        "new-message",
        {
            "message": message,
            "sender_id": request.user.id,
            "sender_name": request.user.username,  # Add the sender's username
        },
    )
    return JsonResponse({"status": "Message sent successfully."})


def get_chat_channel_name(user_id, receiver_room_slug):
    # Ensure the lower ID always comes first in the channel name
    return receiver_room_slug


@login_required
def chat_history(request, receiver_room_slug):
    messages = ChatRoom3.objects.filter(
        sender=request.user, receiver=receiver_room_slug
    )
    return JsonResponse(list(messages), safe=False)
