from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, UserView, GoalViewSet,
    UserProfileViewSet,
    LessonProgressViewSet,
    AchievementViewSet,
    LocalConfigViewSet,
    MyProfileView,
)
from .views_sync import SyncView

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'lessons', LessonProgressViewSet, basename='lesson')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'configs', LocalConfigViewSet, basename='config')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserView.as_view(), name='me'),
    path('me/profile/', MyProfileView.as_view(), name='my-profile'),
    path('sync/', SyncView.as_view(), name='sync'),
    path('', include(router.urls)),
]

