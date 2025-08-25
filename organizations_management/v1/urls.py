from django.urls import include, path
from rest_framework import routers

from organizations_management.v1 import views


router = routers.DefaultRouter()
router.register(r'', views.OrganizationViewSet, basename='organizations')

urlpatterns = [
    path(r'organizations', include(router.urls))
]