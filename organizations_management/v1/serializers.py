from rest_framework import serializers

from files import models as files_models
from organizations_management import models


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        exclude = ['created_at', 'updated_at', 'owner', 'members', 'admins']


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        exclude = ['created_at', 'updated_at', 'owner']


class OrganizationAddRemoveMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Organization
        fields = ['members']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = '__all__'


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        exclude = ['created_at', 'updated_at', 'organization']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        exclude = ['created_at', 'updated_at', 'organization']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'


class GenerateFileUploadUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = files_models.File
        fields = ['filename', 'mime_type']


class FileUploadUrlSerializer(serializers.Serializer):
    url = serializers.CharField()
    file_id = serializers.CharField()
