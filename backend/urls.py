from django.urls import include, path

from . import views

# app_name = 'backend'
urlpatterns = [
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.register_user, name="register"),
    path("interest-list", views.interest_list, name="interest_list"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("users/<str:username>/", views.user_detail, name="user_detail"),
    path("search/", views.search_results, name="search_results"),
    path("index", views.index_with_categories_view, name="index"),
    path(
        "category/<str:category>/", views.events_by_category, name="events_by_category"
    ),
    # AJAX
    path("events/<int:event_id>/add-interest/", views.add_interest),
    path("events/<int:event_id>/remove-interest/", views.remove_interest),
]
