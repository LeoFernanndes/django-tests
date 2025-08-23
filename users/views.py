from django.shortcuts import render
from rest_framework import viewsets, permissions as drf_permissions

from users import models
from users import permissions
from users import serializers


class UserViewset(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    
    # TODO: check if there are better ways of setting permissions by action
    # TODO: check if this approach breaks any internal logic
    def get_permissions(self):
        if self.action == 'create':
            return [drf_permissions.AllowAny()]
        if self.action == 'list':
            return [drf_permissions.IsAdminUser()]
        return [permissions.IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        elif self.action == 'update':
            return serializers.UserUpdateSerializer
        return serializers.UserSerializer
