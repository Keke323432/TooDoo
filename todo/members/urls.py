from django.urls import path
from members.views import RegisterView, UserEditView,MyPasswordChangeView,DeleteProfilePic
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView







urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('edit_profile/',UserEditView.as_view(), name='edit_profile'),
    path('password/', MyPasswordChangeView.as_view(template_name='registration/change_password.html'), name='change_password'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/change_password_done.html'), name='change_password_done'),
    path('delete_profile_pic/',DeleteProfilePic.as_view(), name='delete_profile_pic'),
  ] 
