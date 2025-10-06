from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('inProgress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    text = models.CharField(max_length=255)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.text}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    total_conversation_time = models.PositiveIntegerField(default=0)  # segundos
    completed_lessons = models.PositiveIntegerField(default=0)
    credits = models.PositiveIntegerField(default=0)
    avatar = models.CharField(max_length=50, blank=True, null=True)
    theme = models.CharField(max_length=30, default='default')
    wants_to_be_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.username}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    topic = models.CharField(max_length=100)
    current_step = models.PositiveIntegerField(default=1)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.username} - {self.topic}"


class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievements")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class LocalConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="configs")
    key = models.CharField(max_length=100)
    value = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'key')

    def __str__(self):
        return f"{self.user.username} - {self.key}"
