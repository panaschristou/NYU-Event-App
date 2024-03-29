from django.urls import include, path

from . import views

# app_name = 'backend'
urlpatterns = [
    path("login", views.base.login_user, name="login"),
    path("logout", views.base.logout_user, name="logout"),
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
        views.review_handler.post_review,
        name="post_review",
    ),
    path("users/<str:username>/", views.base.user_detail, name="user_detail"),
    path("profile-edit/", views.profile_handlers.profile_edit, name="profile_edit"),
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
    path("logout/", views.base.logout_user, name="logout"),
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
]
