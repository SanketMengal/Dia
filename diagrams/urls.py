from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from . import views

urlpatterns = [
    # Root → redirect to login page
    path("", RedirectView.as_view(url=reverse_lazy('login'), permanent=False), name="home"),

    # Replace default login view with company SSO login view
    path(
        "login/",
        views.company_sso_login_view,
        name="login"
    ),
    # Signup page hidden (disabled)
    # path("signup/", views.signup_view, name="signup"),

    # Main authenticated pages
    path("gallery/", views.gallery_view, name="gallery"),
    path("editor/", views.editor_view, name="editor"),
    path("analytics/", views.analytics_view, name="analytics"),
    path('about/', views.about_view, name='about'),

    # Diagram CRUD
    path("diagram/create/", views.diagram_create, name="diagram_create"),
    path("diagram/edit/<int:diagram_id>/", views.diagram_edit, name="diagram_edit"),
    path("diagram/delete/<int:diagram_id>/", views.diagram_delete, name="diagram_delete"),

    # Logout
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),

    # Users list and sending requests
    path("users/", views.users, name="users"),
    path("users/send-request/<int:user_id>/", views.send_request_view, name="send_request"),

    # Handle access request actions (accept/decline)
    path("requests/handle/<int:req_id>/", views.handle_request_view, name="handle_request"),
]
