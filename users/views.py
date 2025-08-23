from django.shortcuts import render
from rest_framework import viewsets

from users import models
from users import serializers


class UserViewset(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        elif self.action == 'update':
            return serializers.UserUpdateSerializer
        return serializers.UserSerializer
