from django.urls import path

from . import views

# app_name = 'backend'
urlpatterns = [
    path('login',views.login_user, name="login"),
    path('register',views.register_user, name="register"),
    path('',views.index, name="index"),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('search/', views.search_results, name='search_results'),
]