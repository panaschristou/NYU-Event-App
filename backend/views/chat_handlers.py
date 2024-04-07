# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from backend.models import Chat
from backend.views.pusher_config import pusher_client
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse


@login_required
def chat_index(request):
    current_user = request.user
    users_with_chats = User.objects.filter(
        Q(sent_chats__receiver=current_user) | Q(received_chats__sender=current_user)
    ).distinct()

    # Prepare a dictionary with user data to pass to the template
    user_data = {user.id: user for user in users_with_chats}

    context = {
        "users_with_data": user_data,
        "current_user_id": current_user.id,  # Pass the current user's ID to the context
    }
    return render(request, "chat_index.html", context)


@login_required
@require_POST
def send_message(request):
    sender = request.user
    receiver_id = request.POST.get("receiver_id")
    message = request.POST.get("message")
    receiver = User.objects.get(id=receiver_id)
    # save the message to the database
    receiver_id = int(receiver_id)

    chat_message = Chat.objects.create(
        sender=sender, receiver=receiver, message=message
    )

    # Trigger a Pusher event
    channel_name = get_chat_channel_name(request.user.id, receiver_id)
    pusher_client.trigger(
        channel_name,
        "new-message",
        {
            "message": message,
            "sender_id": request.user.id,
            "sender_name": request.user.username,  # Add the sender's username
            "timestamp": chat_message.timestamp.strftime("%B %d, %Y, %I:%M %p"),
        },
    )
    return JsonResponse({"status": "Message sent successfully."})


def get_chat_channel_name(user_id1, user_id2):
    # Ensure the lower ID always comes first in the channel name
    if user_id1 > user_id2:
        user_id1, user_id2 = user_id2, user_id1
    return f"private-chat-{user_id1}-{user_id2}"


@login_required
def get_chat(request):
    receiver_id = request.GET.get("user_id")
    # other_user = get_object_or_404(User, pk=receiver_id)
    receiver_name = User.objects.get(id=receiver_id).username
    chat_messages = Chat.objects.filter(
        Q(sender=request.user, receiver_id=receiver_id)
        | Q(sender_id=receiver_id, receiver=request.user)
    ).order_by("timestamp")

    return render(
        request,
        "components/chat_window.html",
        {
            "user_id": request.user.id,
            "receiver_id": receiver_id,
            "chat_messages": chat_messages,
            "receiver_name": receiver_name,
        },
    )
