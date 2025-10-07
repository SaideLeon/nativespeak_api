from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Goal, UserProfile, LessonProgress, Achievement, LocalConfig
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField()
        self.fields['username'].required = False

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs):
        attrs['username'] = User.objects.get(email=attrs['email']).username
        data = super().validate(attrs)
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    terms = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'password2', 'terms')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        if not attrs['terms']:
            raise serializers.ValidationError({"terms": "You must accept the terms of service."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'text', 'status', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user"]


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = "__all__"
        read_only_fields = ["user"]


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"
        read_only_fields = ["user", "unlocked_at"]


class LocalConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalConfig
        fields = "__all__"
        read_only_fields = ["user", "updated_at"]


class AdminRequestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user, wants_to_be_admin=True)
        return user
