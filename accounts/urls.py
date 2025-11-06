from django.urls import path
from .views import ProfileUpdateView
from django.contrib.auth.views import LogoutView,LoginView
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('profile/',ProfileUpdateView.as_view(),name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/confirm/', LogoutConfirmView.as_view(), name='logout_confirm'),
    path('signup/', SignupView.as_view(), name='signup'),
]

