from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView,PasswordChangeView
from django.views.generic import CreateView, UpdateView,DeleteView
from .forms import SignUpForm, ProfilePageForm, PasswordsChangeForm
from todo_project.models import Profile





class RegisterView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login') 
    
    
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    
class CustomLogoutView(LogoutView):
    pass  



class UserEditView(UpdateView):
    form_class = ProfilePageForm
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy('edit_profile') 
    
    def get_object(self):
        # Get the profile instance for the current user, or create a new one if it doesn't exist
        profile, created = Profile.objects.get_or_create(user=self.request.user)      #  study this
        return profile
    
class MyPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('change_password_done')
    form_class = PasswordsChangeForm


class DeleteProfilePic(DeleteView):
    template_name = 'registration/delete_profile_pic.html'
    success_url = reverse_lazy('edit_profile')
    
    