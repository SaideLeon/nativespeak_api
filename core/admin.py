from django.contrib import admin
from .models import Goal, UserProfile, LessonProgress, Achievement, LocalConfig
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


@admin.register(Goal)
class GoalAdmin(ModelAdmin):
    list_display = ('id', 'user', 'text', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('text', 'user__username')

@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'wants_to_be_admin', 'credits', 'completed_lessons', 'total_conversation_time', 'theme')
    search_fields = ('user__username', 'user__email', 'theme')
    list_filter = ('wants_to_be_admin', 'theme', 'user__is_staff')
    ordering = ('user__username',)
    actions = ['make_admin']

    @admin.action(description='Approve selected users as admins')
    def make_admin(self, request, queryset):
        for profile in queryset:
            profile.user.is_staff = True
            profile.user.save()
            profile.wants_to_be_admin = False
            profile.save()


class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_filter = BaseUserAdmin.list_filter + ('is_staff',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(LessonProgress)
class LessonProgressAdmin(ModelAdmin):
    list_display = ('user', 'topic', 'current_step', 'completed')
    search_fields = ('user__username', 'topic')
    list_filter = ('completed',)
    ordering = ('user__username', 'topic')


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    list_display = ('user', 'name', 'unlocked_at')
    search_fields = ('user__username', 'name')
    list_filter = ('unlocked_at',)
    ordering = ('-unlocked_at',)


@admin.register(LocalConfig)
class LocalConfigAdmin(ModelAdmin):
    list_display = ('user', 'key', 'updated_at')
    search_fields = ('user__username', 'key')
    list_filter = ('updated_at',)
    ordering = ('-updated_at',)