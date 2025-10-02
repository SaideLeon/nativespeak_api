from rest_framework import serializers
from .models import Setting, Tool, LogEntry, Achievement, Notification, Presence, TodoItem, Lesson, UIState

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ['id', 'key', 'value']

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'config', 'enabled']

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = ['id', 'timestamp', 'entry']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'unlocked', 'metadata']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'created_at', 'read']

class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = ['id', 'user_id', 'status', 'last_seen']

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TodoItem
        fields = ['id', 'text', 'completed', 'created_at']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'slug', 'title', 'content']

class UIStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UIState
        fields = ['id', 'key', 'state']


class AuthRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text='User email address; will be used as the username (e.g. user@example.com)', label='Email')
    password = serializers.CharField(write_only=True, help_text='Password for the new account (e.g. a strong passphrase)', label='Password')
    first_name = serializers.CharField(allow_blank=True, required=False, help_text='First name (optional) (e.g. João)', label='First name')
    last_name = serializers.CharField(allow_blank=True, required=False, help_text='Last name (optional) (e.g. Silva)', label='Last name')


class AuthLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text='User email address (e.g. user@example.com)', label='Email')
    password = serializers.CharField(write_only=True, help_text='User password (e.g. your account password)', label='Password')
