from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from core import views

router = routers.DefaultRouter()
router.register(r'settings', views.SettingsViewSet, basename='settings')
router.register(r'tools', views.ToolViewSet)
router.register(r'logs', views.LogEntryViewSet)
router.register(r'achievements', views.AchievementViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'presence', views.PresenceViewSet)
router.register(r'todos', views.TodoViewSet)
router.register(r'lessons', views.LessonViewSet, basename='lessons')
router.register(r'ui-state', views.UIStateViewSet, basename='ui-state')
router.register(r'auth', views.AuthViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # OpenAPI schema and a simple docs UI (DRF's built-in views)
    path('api/schema/', get_schema_view(title='NativeSpeak API', description='API for NativeSpeak', version='1.0.0'), name='openapi-schema'),
    path('api/docs/', TemplateView.as_view(template_name='rest_framework/docs.html', extra_context={'schema_url':'openapi-schema'}), name='api_docs'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', views.home, name='home'),
]
