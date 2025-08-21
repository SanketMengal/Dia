# diagrams/admin.py

from django.contrib import admin
from .models import Diagram # Import the model you want to register

# Register your models here.
admin.site.register(Diagram)