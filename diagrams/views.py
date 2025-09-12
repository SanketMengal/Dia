from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, Http404
from .models import Diagram, AccessRequest
import json
import requests
import logging

from rest_framework import viewsets, permissions
from .serializers import DiagramSerializer

logger = logging.getLogger(__name__)

# -------------------------------
# Main Pages
# -------------------------------

@login_required
def gallery_view(request):
    own_diagrams = Diagram.objects.filter(author=request.user)
    shared_diagrams = Diagram.objects.filter(shared_with=request.user)
    diagrams = (own_diagrams | shared_diagrams).distinct()

    pending_requests = request.user.received_requests.filter(is_accepted=None).select_related('from_user')
    accepted_requests = request.user.received_requests.filter(is_accepted=True).select_related('from_user')
    accepted_users = [ar.from_user for ar in accepted_requests]

    return render(request, "Gallery.html", {
        'diagrams': diagrams,
        'pending_requests': pending_requests,
        'accepted_users': accepted_users,
    })

@login_required
def editor_view(request, diagram_id=None):
    diagram = None
    if diagram_id:
        diagram = get_object_or_404(Diagram, id=diagram_id, author=request.user)
    return render(request, "Editor.html", {'diagram': diagram})

@login_required
def analytics_view(request):
    return render(request, "Analytics.html")

# -------------------------------
# CRUD Operations
# -------------------------------

@login_required
def diagram_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        mermaid_code = request.POST.get('mermaid_code')
        diagram_data_raw = request.POST.get('diagram_data', '{}')

        if title and mermaid_code:
            try:
                diagram_data = json.loads(diagram_data_raw)
            except Exception:
                diagram_data = {}

            diagram = Diagram(
                title=title,
                mermaid_code=mermaid_code,
                diagram_data=diagram_data,
                author=request.user
            )
            diagram.save()
            return redirect('gallery')

    return render(request, 'diagram_form.html')

@login_required
def diagram_edit(request, diagram_id):
    diagram = get_object_or_404(Diagram, id=diagram_id, author=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        mermaid_code = request.POST.get('mermaid_code')
        diagram_data_raw = request.POST.get('diagram_data', '{}')

        if title and mermaid_code:
            try:
                diagram_data = json.loads(diagram_data_raw)
            except Exception:
                diagram_data = {}

            diagram.title = title
            diagram.mermaid_code = mermaid_code
            diagram.diagram_data = diagram_data
            diagram.save()
            return redirect('gallery')

    return render(request, 'diagram_form.html', {'diagram': diagram})

@login_required
def diagram_delete(request, diagram_id):
    diagram = get_object_or_404(Diagram, id=diagram_id, author=request.user)

    if request.method == 'POST':
        diagram.delete()
        return redirect('gallery')

    return render(request, 'diagram_confirm_delete.html', {'diagram': diagram})

# -------------------------------
# Authentication
# -------------------------------

def company_sso_login_view(request):
    """
    Login view that first authenticates locally if user exists.
    If not, verifies username/password with company API,
    creates user locally with company info and logs in.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'login.html')

        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()

        if user:
            # Local user exists, authenticate locally
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('gallery')
            else:
                messages.error(request, 'Invalid username or password.')
                return render(request, 'login.html')

        else:
            # User not found locally, verify with company API
            print(f"[DEBUG] Calling company API for user: {username}")
            try:
                response = requests.post(
                    'https://api-sso.synth365.com/token',
                    json={'username': username, 'password': password},
                    timeout=5,
                )
                print(f"[DEBUG] Company API response status code: {response.status_code}")
                print(f"[DEBUG] Company API response text: {response.text}")
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                print(f"[ERROR] Failed to reach Company SSO service: {e}")
                messages.error(request, 'Failed to reach Company SSO service.')
                return render(request, 'login.html')

            if 'token' not in data:
                print(f"[DEBUG] Company API did not return token. Invalid credentials for user: {username}")
                messages.error(request, 'Invalid company credentials.')
                return render(request, 'login.html')

            authorized_username = data.get('user_username')
            if authorized_username != username:
                print(f"[DEBUG] User is not authorized according to company API: got '{authorized_username}', expected '{username}'")
                messages.error(request, 'User is not authorized.')
                return render(request, 'login.html')

            email = data.get('user_email', '')
            full_name = data.get('user_fullname', '')
            first_name = ''
            last_name = ''
            if full_name:
                parts = full_name.split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''

            try:
                user = user_model.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                print(f"[DEBUG] Created new user: {username}")
            except Exception as e:
                print(f"[ERROR] Error creating user {username}: {e}")
                messages.error(request, f'Error creating user: {e}')
                return render(request, 'login.html')

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('gallery')
            else:
                print(f"[ERROR] Authentication failed after creating user: {username}")
                messages.error(request, 'Authentication failed after user creation.')
                return render(request, 'login.html')

    else:
        return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

# -------------------------------
# Users and Access Requests
# -------------------------------

@login_required
def users(request):
    users_list = User.objects.exclude(id=request.user.id).order_by('username')
    pending_sent_user_ids = list(
        AccessRequest.objects.filter(from_user=request.user, is_accepted=None)
        .values_list('to_user_id', flat=True)
    )
    return render(request, 'user.html', {
        'users': users_list,
        'pending_sent_user_ids': pending_sent_user_ids,
    })

@login_required
@require_POST
def send_request_view(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    from_user = request.user

    if from_user == to_user:
        messages.error(request, "You cannot send a request to yourself.")
        return redirect('users')

    if AccessRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        messages.info(request, "You have already sent a request to this user.")
        return redirect('users')

    AccessRequest.objects.create(from_user=from_user, to_user=to_user)
    messages.success(request, f"Access request sent to {to_user.username}")
    return redirect('users')

@login_required
@require_POST
def handle_request_view(request, req_id):
    req = get_object_or_404(AccessRequest, id=req_id, to_user=request.user)
    action = request.POST.get('action')

    if action == 'accept':
        req.is_accepted = True
        diagrams = Diagram.objects.filter(author=request.user)
        for diagram in diagrams:
            diagram.shared_with.add(req.from_user)
        req.save()
        messages.success(request, f"Accepted access request from {req.from_user.username}.")
    elif action == 'decline':
        req.is_accepted = False
        req.save()
        messages.info(request, f"Declined access request from {req.from_user.username}.")
    else:
        messages.error(request, "Invalid action.")

    return redirect('gallery')

def about_view(request):
    return render(request, 'About.html')

# -------------------------------
# REST API ViewSet

class DiagramViewSet(viewsets.ModelViewSet):
    serializer_class = DiagramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Diagram.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
