from django.urls import path
from .views import ProfileUpdateView, LogoutConfirmView, CustomLoginView, SignupView
from django.contrib.auth.views import LogoutView,LoginView
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('profile/',ProfileUpdateView.as_view(),name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/confirm/', LogoutConfirmView.as_view(), name='logout_confirm'),
    path('signup/', SignupView.as_view(), name='signup'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view (template_name='password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]

