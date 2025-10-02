from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Setting, Tool, LogEntry, Achievement, Notification, Presence, TodoItem, Lesson, UIState


@admin.register(Setting)
class SettingAdmin(ModelAdmin):
	list_display = ("key",)
	search_fields = ("key",)


@admin.register(Tool)
class ToolAdmin(ModelAdmin):
	list_display = ("name", "enabled")
	search_fields = ("name",)
	list_filter = ("enabled",)


@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
	list_display = ("timestamp",)
	readonly_fields = ("timestamp",)


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
	list_display = ("name", "unlocked")
	list_filter = ("unlocked",)
	search_fields = ("name",)


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
	list_display = ("title", "type", "created_at", "read")
	list_filter = ("type", "read")
	search_fields = ("title",)


@admin.register(Presence)
class PresenceAdmin(ModelAdmin):
	list_display = ("user_id", "status", "last_seen")
	search_fields = ("user_id",)


@admin.register(TodoItem)
class TodoItemAdmin(ModelAdmin):
	list_display = ("text", "completed", "created_at")
	list_filter = ("completed",)
	search_fields = ("text",)


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
	list_display = ("slug", "title")
	search_fields = ("slug", "title")


@admin.register(UIState)
class UIStateAdmin(ModelAdmin):
	list_display = ("key",)
	search_fields = ("key",)
