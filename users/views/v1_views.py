from decouple import config
from drf_spectacular.utils import extend_schema
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, filters, generics, mixins, pagination, response, permissions as drf_permissions, views, viewsets

from files import models as files_models
from organizations_management.helpers import generate_upload_presigned_url
from users import models
from users import permissions
from users.serializers import v1_serializers


USER_PROFILE_IMAGES_BUCKET  = config('USER_PROFILE_IMAGES_BUCKET')


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
        elif self.action == 'list':
            return [drf_permissions.AllowAny()]
        elif self.action in ('retrieve_self', 'update_self'):
            return [drf_permissions.IsAuthenticated()]
        return [permissions.IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == 'create':
            return v1_serializers.UserCreateSerializer
        elif self.action == 'update':
            return v1_serializers.UserUpdateSerializer
        elif self.action == 'update_self':
            return v1_serializers.UserUpdateSelfSerializer
        return v1_serializers.UserSerializer

    def get_queryset(self):
        return super().get_queryset().order_by('date_joined') # order is overriden by ordering but filter keep being properly applied

    @decorators.action(detail=False, methods=['GET'], name='Retrieve self user')
    def retrieve_self(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=['POST'], name='Update self user')
    def update_self(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(serializer.data)


class UserImageUploadView(views.APIView):

    permission_classes = [drf_permissions.IsAuthenticated]

    @extend_schema(
            request=v1_serializers.GenerateProfileImageUploadUrlSerializer,
            responses={
                200: v1_serializers.ProfileImageUploadUrlSerializer
            }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = v1_serializers.GenerateProfileImageUploadUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key = f'{user.id}/{serializer.data["filename"]}'
        file = files_models.File(filename=serializer.data["filename"], filetype='image', bucket=USER_PROFILE_IMAGES_BUCKET, location=key)
        file.save()
        presigned_url = generate_upload_presigned_url(bucket_name=USER_PROFILE_IMAGES_BUCKET, location=key, content_type=serializer.data['content_type'], expiration=900)
        response_serializer = v1_serializers.ProfileImageUploadUrlSerializer({'url': presigned_url, 'file_id': file.id})
        return response.Response(response_serializer.data)
