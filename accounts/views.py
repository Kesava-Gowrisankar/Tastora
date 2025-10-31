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
    
class LogoutConfirmView(TemplateView):
    template_name = "logout.html"

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('recipe:home')

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("recipe:home")  # Redirect to home or wherever after login

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in
        login(self.request, self.object)
        return response      
