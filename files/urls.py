from django.urls import include, path
from rest_framework import routers

from files import views


router = routers.DefaultRouter()
router.register(r'', views.FileViewSet, basename='files')

urlpatterns = [
    path(r'files/', include(router.urls))
]