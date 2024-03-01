from django.urls import include, path

from . import views

# app_name = 'backend'
urlpatterns = [
    path('login',views.login_user, name="login"),
    path('register',views.register_user, name="register"),
    path('',views.index, name="index"),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]