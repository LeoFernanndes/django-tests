from django.urls import include, path
from rest_framework import routers

from users.views import v1_views


router = routers.DefaultRouter()
router.register(r'users', v1_views.UserViewset, basename='users') 

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += router.urls
