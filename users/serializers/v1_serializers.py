from rest_framework import serializers

from users import models 


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