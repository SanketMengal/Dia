from rest_framework import serializers
from .models import Diagram

class DiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = ['id', 'title', 'mermaid_code', 'diagram_data', 'created_at', 'updated_at', 'author']
        read_only_fields = ['author', 'created_at', 'updated_at']
