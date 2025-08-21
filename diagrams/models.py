from django.db import models
from django.contrib.auth.models import User

class Diagram(models.Model):
    """
    A model to store user-created diagrams.
    """
    title = models.CharField(max_length=200)
    mermaid_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
