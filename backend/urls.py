from django.urls import path

from . import views

# app_name = 'backend'
urlpatterns = [
    path('login',views.login_user, name="login"),
    path('register',views.register_user, name="register"),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('search/', views.search_results, name='search_results'),
    path('', views.index_with_categories_view, name="index"),
    path('category/<str:category>/', views.events_by_category, name='events_by_category'),
]