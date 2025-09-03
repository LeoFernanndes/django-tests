from django.shortcuts import get_object_or_404
from rest_framework import permissions

from organizations_management import models


class OrganizationOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class OrganizationAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.admins.all() or request.user == obj.owner
 

class OrganizationMemberPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.members.all() or request.user in obj.admins.all() or request.user == obj.admin
 