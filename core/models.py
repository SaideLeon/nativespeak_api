from django.db import models

class Setting(models.Model):
    key = models.CharField(max_length=200, unique=True)
    value = models.JSONField()

    def __str__(self):
        return self.key

class Tool(models.Model):
    name = models.CharField(max_length=200)
    config = models.JSONField()
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    entry = models.JSONField()

class Achievement(models.Model):
    name = models.CharField(max_length=200)
    unlocked = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)

class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    type = models.CharField(max_length=50, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Presence(models.Model):
    user_id = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=50, default='online')
    last_seen = models.DateTimeField(auto_now=True)

class TodoItem(models.Model):
    text = models.CharField(max_length=500)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Lesson(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    content = models.JSONField()

class UIState(models.Model):
    key = models.CharField(max_length=200, unique=True)
    state = models.JSONField()

