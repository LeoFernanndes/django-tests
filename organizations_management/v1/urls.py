from django.urls import include, path
from rest_framework import routers

from organizations_management.v1 import views


router = routers.DefaultRouter()
router.register(r'', views.OrganizationViewSet, basename='organizations')

projects_router = routers.DefaultRouter()
projects_router.register(r'', views.ProjectViewSet, basename='projects')

files_router = routers.DefaultRouter()
files_router.register(r'', views.OrganizationFilesViewSet, basename='files')

urlpatterns = [
    path(r'organizations/', include(router.urls)),
    path(r'organizations/<organization_id>/projects/', include(projects_router.urls)),
    path(r'organizations/<organization_id>/files/', include(files_router.urls)),
    path(f'organizations/<organization_id>/generate-file-upload-presigned-url', views.OrganizationFileUploadView.as_view())
]