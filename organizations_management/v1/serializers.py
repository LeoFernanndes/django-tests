from rest_framework import serializers

from organizations_management import models


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        exclude = ['created_at', 'updated_at', 'owner']


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        exclude = ['created_at', 'updated_at', 'owner']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = '__all__'