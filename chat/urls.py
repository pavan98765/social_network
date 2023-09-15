from django.urls import path
from chat import views as chat_views

urlpatterns = [
    path("chat/<int:receiver_id>/", chat_views.chat, name="chat"),
    path(
        "send_message/<int:receiver_id>/", chat_views.send_message, name="send_message"
    ),
    path("inbox/", chat_views.inbox, name="inbox"),
    path(
        "chat/<int:receiver_id>/fetch_latest_messages/",
        chat_views.fetch_latest_messages,
        name="fetch_latest_messages",
    ),
]
