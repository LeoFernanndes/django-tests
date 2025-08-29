from django.urls import include, path
from rest_framework import routers

from organizations_management.v1 import views


router = routers.DefaultRouter()
router.register(r'', views.OrganizationViewSet, basename='organizations')

projects_router = routers.DefaultRouter()
projects_router.register(r'', views.ProjectViewSet, basename='projects')

urlpatterns = [
    path(r'organizations', include(router.urls)),
    path(r'organizations/<organization_id>/projects', include(projects_router.urls)),
]