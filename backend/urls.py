from django.urls import include, path

from . import views

from backend.views import group_chat_handlers
from backend.views import chat_handlers

# app_name = 'backend'
urlpatterns = [
    path("login", views.base.login_user, name="login"),
    path("register", views.base.register_user, name="register"),
    path("delete-account", views.base.delete_user, name="delete_account"),
    path(
        "interest-list",
        views.interest_list_handlers.interest_list,
        name="interest_list",
    ),
    path("activate/<uidb64>/<token>", views.base.activate, name="activate"),
    path("events/<int:event_id>/", views.base.event_detail, name="event_detail"),
    path(
        "events/<int:event_id>/post-review/",
        views.review_handlers.post_review,
        name="post_review",
    ),
    path(
        "events/<int:event_id>/avg-rating/",
        views.review_handlers.get_average_rating,
        name="get_average_rating",
    ),
    path(
        "events/<int:event_id>/display-reviews/",
        views.review_handlers.get_reviews_for_event,
        name="event_reviews",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/likes/",
        views.review_handlers.like_review,
        name="like_review",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/unlike/",
        views.review_handlers.unlike_review,
        name="unlike_review",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/delete/",
        views.review_handlers.delete_review,
        name="delete_review",
    ),
    path(
        "users/<str:username>/reviewhistory/",
        views.review_handlers.get_user_reviews,
        name="reviewhistory",
    ),
    path(
        "users/<str:username>/reviewhistory/<int:review_id>/delete/",
        views.review_handlers.delete_reviewhistory,
        name="delete_reviewhistory",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/reply/",
        views.review_handlers.reply_to_review,
        name="reply_to_review",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/display-replies/",
        views.review_handlers.get_replies_for_review,
        name="display_replies",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/display-replies/<int:reply_id>/like/",
        views.review_handlers.like_reply,
        name="like_replies",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/display-replies/<int:reply_id>/unlike/",
        views.review_handlers.unlike_reply,
        name="unlike_replies",
    ),
    path(
        "events/<int:event_id>/display-reviews/<int:review_id>/display-replies/<int:reply_id>/delete/",
        views.review_handlers.delete_reply,
        name="delete_replies",
    ),
    path("users/<str:username>/", views.base.user_detail, name="user_detail"),
    path("profile-edit/", views.profile_handlers.profile_edit, name="profile_edit"),
    path(
        "profile-edit/avatar",
        views.profile_handlers.upload_avatar,
        name="profile_edit_avatar",
    ),
    path("search/", views.base.search_results, name="search_results"),
    path("search_history/", views.base.search_history, name="search_history"),
    path(
        "delete_search/<int:search_id>/",
        views.base.delete_search_view,
        name="delete_search",
    ),
    path("clear_history/", views.base.clear_history_view, name="clear_history"),
    path("index", views.base.index_with_categories_view, name="index"),
    path(
        "category/<str:category>/",
        views.base.events_by_category,
        name="events_by_category",
    ),
    # AJAX
    path(
        "events/<int:event_id>/add-interest/",
        views.interest_list_handlers.add_interest,
        name="interest_list_handlers.add_interest",
    ),
    path(
        "events/<int:event_id>/remove-interest/",
        views.interest_list_handlers.remove_interest,
        name="interest_list_handlers.remove_interest",
    ),
    path("recent_searches/", views.base.recent_searches, name="recent_searches"),
    # chat1-1
    path("chat/", views.chat_handlers.chat_index, name="chat_index"),
    path(
        "chat/send_message/",
        views.chat_handlers.send_message,
        name="send_message",
    ),
    path("chat/get_chat/", views.chat_handlers.get_chat, name="get_chat"),
    # group chat
    path("rooms/", views.group_chat_handlers.group_chat_index, name="search_rooms"),
    path(
        "chat/<str:receiver_room_slug>/",
        views.group_chat_handlers.chat_with_room,
        name="chat_with_room",
    ),
    path(
        "chat/<str:receiver_room_slug>/send_message/",
        views.group_chat_handlers.send_message,
        name="send_message",
    ),
]
