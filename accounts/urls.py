from django.urls import path
from .views import ProfileUpdateView, LogoutConfirmView, CustomLoginView, SignupView
from django.contrib.auth.views import LogoutView,LoginView
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('profile/',ProfileUpdateView.as_view(),name='profile'),
]
