# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from backend.models import Chat
from backend.views.pusher_config import pusher_client
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.views.decorators.http import require_POST


@login_required
def chat_index(request):
    # Assuming we want to chat with all other users for simplicity
    users = User.objects.exclude(id=request.user.id)  # Exclude the current user
    return render(request, "chat_index.html", {"users": users})


@login_required
def chat_with_user(request, receiver_id):
    chat_messages = Chat.objects.filter(
        Q(sender=request.user, receiver_id=receiver_id)
        | Q(sender_id=receiver_id, receiver=request.user)
    ).order_by("timestamp")

    return render(
        request,
        "chat_with_user.html",
        {
            "user_id": request.user.id,
            "receiver_id": receiver_id,
            "chat_messages": chat_messages,
        },
    )


@login_required
@require_POST
def send_message(request, receiver_id):
    sender = request.user
    # receiver = request.POST.get('receiver_id')
    message = request.POST.get("message")
    receiver = User.objects.get(id=receiver_id)
    # save the message to the database
    Chat.objects.create(sender=sender, receiver=receiver, message=message)

    # Trigger a Pusher event
    channel_name = get_chat_channel_name(request.user.id, receiver_id)
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


def get_chat_channel_name(user_id1, user_id2):
    # Ensure the lower ID always comes first in the channel name
    if user_id1 > user_id2:
        user_id1, user_id2 = user_id2, user_id1
    return f"private-chat-{user_id1}-{user_id2}"


@login_required
def chat_history(request, receiver_id):
    messages = Chat.objects.filter(
        sender=request.user, receiver=receiver_id
    ) | Chat.objects.filter(sender=receiver_id, receiver=request.user)
    messages = messages.order_by("timestamp").values(
        "sender", "recipient", "message", "timestamp"
    )
    return JsonResponse(list(messages), safe=False)


def search_users(request):
    if "query" in request.GET:
        query = request.GET["query"]
        users = User.objects.filter(username__icontains=query)
        return render(request, "partials/user_search_results.html", {"users": users})
    else:
        return JsonResponse({"error": "No search term provided"}, status=400)
