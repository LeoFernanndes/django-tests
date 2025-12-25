from rest_framework import serializers

from users import models 
from files import models as files_models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        exclude = ['groups', 'is_staff', 'is_superuser', 'password', 'user_permissions']


class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        exclude = ['date_joined', 'groups', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'user_permissions']


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        exclude = ['date_joined', 'email', 'groups', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'password', 'user_permissions', 'username']


class UserUpdateSelfSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        exclude = ['date_joined', 'email', 'groups', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'password', 'user_permissions', 'username']


class GenerateProfileImageUploadUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = files_models.File
        fields = ['filename', 'mime_type']

class ProfileImageUploadUrlSerializer(serializers.Serializer):
    url = serializers.CharField()
    file_id = serializers.CharField()


class LoginCookieTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class LoginCookieUserResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    username = serializers.CharField()
