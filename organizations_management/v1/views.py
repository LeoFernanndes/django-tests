from django.shortcuts import get_object_or_404
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


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = models.Project.objects.all()
    permission_classes = [rest_framework_permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        organization_id = self.request.parser_context['kwargs']['organization_id']
        if self.action == 'create':
            organization = get_object_or_404(models.Organization.objects.get(id=organization_id, owner=self.request.user.id))
            return super().get_queryset().filter(organization=organization.id)
        return super().get_queryset().filter(organization=organization_id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ProjectCreateSerializer
        if self.action == 'update':
            return serializers.ProjectUpdateSerializer
        return serializers.ProjectSerializer
    
    def perform_create(self, serializer):
        organization = models.Organization.objects.get(id=self.request.parser_context['kwargs']['organization_id'])
        serializer.save(organization=organization)
