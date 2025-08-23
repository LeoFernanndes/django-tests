from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, pagination, permissions as drf_permissions

from users import models
from users import permissions
from users import serializers


class DefaultPageNumberPaginationClass(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000


class UserViewset(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    # is_staff is not available on list serializer but keeps being available on filtering
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]    
    filterset_fields = ['is_active', 'is_staff'] 
    ordering_fields = ['date_joined']
    ordering = ['-date_joined'] # overrides get_queryset ordering
    pagination_class = DefaultPageNumberPaginationClass
    
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

    def get_queryset(self):
        return super().get_queryset().order_by('date_joined') # order is overriden by ordering but filter keep being properly applied
