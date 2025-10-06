from rest_framework import viewsets, permissions, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Goal, UserProfile, LessonProgress, Achievement, LocalConfig
from .serializers import (
    RegisterSerializer, UserSerializer, GoalSerializer,
    UserProfileSerializer,
    LessonProgressSerializer,
    AchievementSerializer,
    LocalConfigSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.generic import TemplateView
from django.views import generic
from django.urls import reverse_lazy
from .forms import AdminRequestForm

class LoginView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={200: openapi.Response(
            description="Access and refresh tokens",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Goal.objects.none()
        return self.request.user.goals.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# --- Permissão personalizada ---
class IsAdminOrReadOnlySelf(permissions.BasePermission):
    """
    Permite que:
    - Admins vejam e editem tudo.
    - Usuários comuns só possam ver/editar o próprio perfil.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user


# --- Base genérica para ViewSets do usuário ---
class BaseUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['id']
    ordering_fields = ['id', 'user__username']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.model.objects.none()
        return self.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- Perfis de usuário (restrito por permissão) ---
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnlySelf]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['user__username', 'user__email', 'theme']
    ordering_fields = ['user__username', 'credits', 'total_conversation_time']
    filterset_fields = ['theme']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserProfile.objects.none()
        user = self.request.user
        if user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)


# --- Outras viewsets sem alteração ---
class LessonProgressViewSet(BaseUserViewSet):
    model = LessonProgress
    serializer_class = LessonProgressSerializer
    search_fields = ['topic']
    filterset_fields = ['completed']
    ordering_fields = ['topic', 'current_step']


class AchievementViewSet(BaseUserViewSet):
    model = Achievement
    serializer_class = AchievementSerializer
    search_fields = ['name']
    ordering_fields = ['unlocked_at']


class LocalConfigViewSet(BaseUserViewSet):
    model = LocalConfig
    serializer_class = LocalConfigSerializer
    search_fields = ['key']
    ordering_fields = ['updated_at']


# --- Endpoint /me/profile ---
class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class KnowView(TemplateView):
    template_name = "know.html"


class IndexView(TemplateView):
    template_name = "index.html"


class AdminRequestView(generic.CreateView):
    form_class = AdminRequestForm
    template_name = 'admin_request.html'
    success_url = reverse_lazy('admin_request_success')

    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.create(user=self.object, wants_to_be_admin=True)
        return response

class AdminRequestSuccessView(generic.TemplateView):
    template_name = 'admin_request_success.html'

