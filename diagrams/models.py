from django.db import models
from django.contrib.auth.models import User


class Diagram(models.Model):
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('unlisted', 'Unlisted (Anyone with link)'),
    ]

    title = models.CharField(max_length=200)
    mermaid_code = models.TextField()
    diagram_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diagrams')

    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_diagrams')

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    class Meta:
        ordering = ['-updated_at']

    def can_be_viewed_by(self, user):
        if self.visibility in ['public', 'unlisted']:
            return True
        if self.author == user:
            return True
        if user.is_authenticated and self.shared_with.filter(id=user.id).exists():
            return True
        return False


class AccessRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(null=True)  # None = pending, True/False = responded

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        status = 'Pending' if self.is_accepted is None else ('Accepted' if self.is_accepted else 'Declined')
        return f"{self.from_user.username} → {self.to_user.username} ({status})"
