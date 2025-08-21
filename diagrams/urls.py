# diagrams/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from . import views

urlpatterns = [
    # Redirects the root URL to the login page
    path("", RedirectView.as_view(url=reverse_lazy('login'), permanent=False), name="home"),
    
    # Login page using Django's built-in LoginView with a specific success URL
    path('login/', auth_views.LoginView.as_view(template_name='login.html', success_url=reverse_lazy('dashboard')), name='login'),
    
    # The home page, which is only accessible to authenticated users
    path('dashboard/', views.index, name="dashboard"),

    # Logout page that redirects to the login page after a user logs out
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
