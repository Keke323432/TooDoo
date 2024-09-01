from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView,PasswordChangeView
from django.views.generic import CreateView, UpdateView,DeleteView, ListView
from .forms import SignUpForm, ProfilePageForm, PasswordsChangeForm
from todo_project.models import Profile
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import get_object_or_404





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
    
    

class UserList(ListView):
    model = User
    context_object_name = 'users'  # Context variable name to use in the template
    template_name = 'registration/user_list.html'
    
    def get_queryset(self):
        # Fetch all users with their related profiles
        return User.objects.select_related('profile').all()

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile  # Assuming the related name for Profile is `profile`
    return render(request, 'registration/user_profile.html', {'profile': profile})


