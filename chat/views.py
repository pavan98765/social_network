from django.shortcuts import render, get_object_or_404, redirect
from .models import Message
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse
from core.models import Profile, Post


def chat(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=receiver
    ) | Message.objects.filter(sender=receiver, receiver=request.user).order_by(
        "timestamp"
    )
    sender = request.user
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    return render(
        request,
        "chat/chat.html",
        {
            "receiver": receiver,
            "messages": messages,
            "sender": sender,
            "user_profile": user_profile,
        },
    )


def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    content = request.POST.get("content")
    message = Message(sender=request.user, receiver=receiver, content=content)
    message.save()
    return redirect("chat", receiver_id=receiver_id)


from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q


def inbox(request):
    user = request.user
    conversations = []

    # Get all unique users who sent or received messages from the current user
    received_users = (
        Message.objects.filter(receiver=user)
        .values_list("sender", flat=True)
        .distinct()
    )
    sent_users = (
        Message.objects.filter(sender=user)
        .values_list("receiver", flat=True)
        .distinct()
    )
    user_ids = set(received_users) | set(sent_users)

    # Retrieve user objects and latest message for each user
    for user_id in user_ids:
        other_user = get_object_or_404(User, id=user_id)
        try:
            latest_message = Message.objects.filter(
                Q(sender=user, receiver=other_user)
                | Q(sender=other_user, receiver=user)
            ).latest("timestamp")
        except ObjectDoesNotExist:
            latest_message = None
        conversations.append((other_user, latest_message))

    # Sort conversations by the timestamp of the latest message
    conversations.sort(key=lambda x: x[1].timestamp if x[1] else None, reverse=True)

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    return render(
        request,
        "chat/inbox.html",
        {"conversations": conversations, "user_profile": user_profile},
    )


from django.http import JsonResponse


def fetch_latest_messages(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=receiver
    ) | Message.objects.filter(sender=receiver, receiver=request.user).order_by(
        "-timestamp"
    )

    # Fetch the latest 10 messages
    messages = messages[:10]

    messages_values = list(messages.values())
    for message in messages_values:
        # Convert datetime to string before sending it as JSON
        message["timestamp"] = str(message["timestamp"])

    return JsonResponse(messages_values, safe=False)
