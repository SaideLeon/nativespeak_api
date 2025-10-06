from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import UserProfile, LessonProgress, Achievement, LocalConfig
from .serializers import (
    UserProfileSerializer,
    LessonProgressSerializer,
    AchievementSerializer,
    LocalConfigSerializer,
)


class SyncView(APIView):
    """
    Permite sincronização completa entre dados locais e servidor.
    - GET: retorna todos os dados do usuário autenticado.
    - POST: substitui ou mescla os dados locais enviados.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        profile, _ = UserProfile.objects.get_or_create(user=user)
        lessons = LessonProgress.objects.filter(user=user)
        achievements = Achievement.objects.filter(user=user)
        configs = LocalConfig.objects.filter(user=user)

        data = {
            "profile": UserProfileSerializer(profile).data,
            "lessons": LessonProgressSerializer(lessons, many=True).data,
            "achievements": AchievementSerializer(achievements, many=True).data,
            "configs": LocalConfigSerializer(configs, many=True).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data

        # --- Perfil ---
        if "profile" in data:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            serializer = UserProfileSerializer(profile, data=data["profile"], partial=True)
            if serializer.is_valid():
                serializer.save(user=user)

        # --- Lição ---
        if "lessons" in data:
            LessonProgress.objects.filter(user=user).delete()
            for lesson in data["lessons"]:
                lesson["user"] = user.id
                serializer = LessonProgressSerializer(data=lesson)
                if serializer.is_valid():
                    serializer.save(user=user)

        # --- Conquistas ---
        if "achievements" in data:
            Achievement.objects.filter(user=user).delete()
            for ach in data["achievements"]:
                ach["user"] = user.id
                serializer = AchievementSerializer(data=ach)
                if serializer.is_valid():
                    serializer.save(user=user)

        # --- Configurações ---
        if "configs" in data:
            LocalConfig.objects.filter(user=user).delete()
            for conf in data["configs"]:
                conf["user"] = user.id
                serializer = LocalConfigSerializer(data=conf)
                if serializer.is_valid():
                    serializer.save(user=user)

        return Response({"detail": "Dados sincronizados com sucesso."}, status=status.HTTP_200_OK)
