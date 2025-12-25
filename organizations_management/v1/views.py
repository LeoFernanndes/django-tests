from typing import Any

from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import decorators, mixins, request, response, views, viewsets
from rest_framework import permissions as rest_framework_permissions

from files import models as files_models
from files import serializers as files_serializers
from organizations_management import models, permissions
from organizations_management.helpers import generate_upload_presigned_url
from organizations_management.v1 import serializers


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = models.Organization.objects.all()
    # permission_classes = [permissions.OrganizationAdminPermission, permissions.OrganizationOwnerPermission]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        # return super().get_queryset().filter(owner=self.request.user.id)
        return super().get_queryset()
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [rest_framework_permissions.AllowAny]
        elif self.action == 'update':
            permission_classes = [permissions.OrganizationAdminPermission]
        if self.action in ('add_member', 'remove_member'):
            permission_classes = [permissions.OrganizationAdminPermission]
        elif self.action == 'delete':
            permission_classes = [permissions.OrganizationOwnerPermission]
        else:
            permission_classes = [rest_framework_permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.OrganizationCreateSerializer
        if self.action == 'update':
            return serializers.OrganizationUpdateSerializer
        if self.action in ('add_member', 'remove_member'):
            return serializers.OrganizationAddRemoveMemberSerializer
        return serializers.OrganizationSerializer

    def perform_create(self, serializer):
        # validated_data inside serializer.save is directly extended with **kwargs
        serializer.save(owner=self.request.user) 

    @decorators.action(detail=True, methods=['PUT'], name='Add organization user')
    def add_member(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['members'].extend(instance.members.all())
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['PUT'], name='Remove organization user')
    def remove_member(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['members'] = [member for member in instance.members.all() if member not in serializer.validated_data['members']]
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(serializer.data)


class OrganizationFileUploadView(views.APIView):

    @extend_schema(
            request=serializers.GenerateFileUploadUrlSerializer,
            responses={
                200: serializers.FileUploadUrlSerializer
            }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = serializers.GenerateFileUploadUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = f"{self.request.parser_context['kwargs']['organization_id']}/{serializer.data['filename']}"
        file = files_models.File.objects.create(filename=serializer.data["filename"], mime_type=serializer.data['mime_type'], bucket=settings.USER_PROFILE_IMAGES_BUCKET, location=key, organization_id=self.request.parser_context['kwargs']['organization_id'])
        presigned_url = generate_upload_presigned_url(bucket_name=settings.FILES_BUCKET, location=key, content_type=serializer.data['mime_type'], expiration=900)
        response_serializer = serializers.FileUploadUrlSerializer({'url': presigned_url, 'file_id': file.id})
        return response.Response(response_serializer.data)


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
        elif self.action == 'update':
            return serializers.ProjectUpdateSerializer
        return serializers.ProjectSerializer
    
    def perform_create(self, serializer):
        organization = models.Organization.objects.get(id=self.request.parser_context['kwargs']['organization_id'])
        serializer.save(organization=organization)


class OrganizationFilesViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
    ):

    # queryset = files_models.File.objects.all()
    serializer_class = files_serializers.FileSerializer
    
    def get_queryset(self):
        return files_models.File.objects.filter(organization_id=self.request.parser_context['kwargs']['organization_id'])