# diagrams/views.py

from django.shortcuts import render, redirect # Import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout # Import logout

@login_required
def index(request):
    """
    Renders the index page.
    This view will only be accessible to logged-in users.
    """
    return render(request, "index.html")

def user_logout(request):
    """
    Logs out the current user and redirects to the login page.
    """
    logout(request)
    return redirect('login_page') # Redirects to the login URL