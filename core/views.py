from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny 
from rest_framework.parsers import JSONParser 
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Setting, Tool, LogEntry, Achievement, Notification, Presence, TodoItem, Lesson, UIState
from .serializers import (
    SettingSerializer, ToolSerializer, LogEntrySerializer, AchievementSerializer,
    NotificationSerializer, PresenceSerializer, TodoSerializer, LessonSerializer, UIStateSerializer
)
from .serializers import AuthRegisterSerializer, AuthLoginSerializer
from django.shortcuts import get_object_or_404, render

class SettingsViewSet(viewsets.ViewSet):
    def list(self, request):
        key = request.query_params.get('key')
        if key:
            qs = Setting.objects.filter(key=key)
        else:
            qs = Setting.objects.all()
        serializer = SettingSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = SettingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def by_key(self, request):
        key = request.query_params.get('key')
        if not key:
            return Response({'detail': 'key required'}, status=400)
        obj = get_object_or_404(Setting, key=key)
        return Response(SettingSerializer(obj).data)

    @action(detail=False, methods=['put'])
    def upsert(self, request):
        key = request.data.get('key')
        value = request.data.get('value')
        if not key:
            return Response({'detail': 'key required'}, status=400)
        obj, created = Setting.objects.update_or_create(key=key, defaults={'value': value})
        return Response(SettingSerializer(obj).data)

class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer

class LogEntryViewSet(viewsets.ModelViewSet):
    queryset = LogEntry.objects.order_by('-timestamp').all()
    serializer_class = LogEntrySerializer

class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.order_by('-created_at').all()
    serializer_class = NotificationSerializer

class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer

class TodoViewSet(viewsets.ModelViewSet):
    queryset = TodoItem.objects.order_by('-created_at').all()
    serializer_class = TodoSerializer

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class UIStateViewSet(viewsets.ViewSet):
    def list(self, request):
        qs = UIState.objects.all()
        serializer = UIStateSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post', 'put'])
    def upsert(self, request):
        key = request.data.get('key')
        state = request.data.get('state')
        if not key:
            return Response({'detail': 'key required'}, status=400)
        obj, created = UIState.objects.update_or_create(key=key, defaults={'state': state})
        return Response(UIStateSerializer(obj).data)

    def create(self, request):
        # route POST /api/ui-state/ to upsert for convenience
        return self.upsert(request)

def home(request):
    """Render the detailed documentary landing page."""
    return render(request, "index.html")


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        if not email or not password:
            return Response({'detail': 'email and password are required'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'user with this email already exists'}, status=400)
        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        return Response({'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}, status=201)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'detail': 'email and password required'}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'invalid credentials'}, status=401)
        if not user.check_password(password):
            return Response({'detail': 'invalid credentials'}, status=401)
        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})


class AuthViewSet(viewsets.ViewSet):
    """Expose register/login under the router so they appear in the API root."""

    def get_permissions(self):
        # Allow unauthenticated users to call register and login so clients can
        # create accounts and obtain tokens. Other actions should use the
        # default IsAuthenticatedOrReadOnly behavior configured in settings.
        if getattr(self, 'action', None) in ('register', 'login'):
            return [AllowAny()]
        return []

    # Provide serializers for the action request bodies so the automatic schema
    # generation can include request body shapes and enable the interactive
    # 'Try it' forms in the docs UI.
    def get_serializer_class(self):
        if getattr(self, 'action', None) == 'register':
            return AuthRegisterSerializer
        if getattr(self, 'action', None) == 'login':
            return AuthLoginSerializer
        return None

    @action(detail=False, methods=['post'])
    def register(self, request):
        # delegate to same logic used in RegisterAPIView
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        if not email or not password:
            return Response({'detail': 'email and password are required'}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({'detail': 'user with this email already exists'}, status=400)
        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        return Response({'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}, status=201)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'detail': 'email and password required'}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'invalid credentials'}, status=401)
        if not user.check_password(password):
            return Response({'detail': 'invalid credentials'}, status=401)
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})

    @action(detail=False, methods=['get'], url_path='register-info')
    def register_info(self, request):
        return Response({
            'description': 'Register a new user. POST JSON: {email, password, first_name?, last_name?}',
            'methods': ['POST']
        })

    @action(detail=False, methods=['get'], url_path='login-info')
    def login_info(self, request):
        return Response({
            'description': 'Login and obtain JWT tokens. POST JSON: {email, password}',
            'methods': ['POST']
        })

