from django.views.generic import UpdateView,TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from recipe.models import Profile
from .forms import ProfileForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')  # Redirect to same page after saving

    def get_object(self, queryset=None):
        # Return the profile of the logged-in user
        return Profile.objects.get_or_create(user=self.request.user)[0]
