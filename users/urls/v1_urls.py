from django.urls import include, path
from rest_framework import routers

from users.views import v1_views


router = routers.DefaultRouter()
router.register(r'', v1_views.UserViewset, basename='users') 


urlpatterns = [
    path('users/', include(router.urls)),
]

