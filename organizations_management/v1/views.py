from rest_framework import permissions as rest_framework_permissions, viewsets

from organizations_management import models
from organizations_management.v1 import serializers


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = models.Organization.objects.all()
    permission_classes = [rest_framework_permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user.id)
            
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.OrganizationCreateSerializer
        if self.action == 'update':
            return serializers.OrganizationUpdateSerializer
        return serializers.OrganizationSerializer

    def perform_create(self, serializer):
        # validated_data inside serializer.save is directly extended with **kwargs
        serializer.save(owner=self.request.user) 
