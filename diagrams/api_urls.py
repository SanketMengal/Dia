from rest_framework.routers import DefaultRouter
from .views import DiagramViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'diagrams', DiagramViewSet, basename='diagram')

urlpatterns = [
    path('', include(router.urls)),
]
