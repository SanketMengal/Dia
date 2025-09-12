from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth system URLs: login, logout, password ... etc
    path('accounts/', include('django.contrib.auth.urls')),

    # Your app URLs (web pages)
    path('', include('diagrams.urls')),

    # API URLs namespaced under /api/
    path('api/', include('diagrams.api_urls')),  # You should create this api_urls.py in diagrams app
     
]
