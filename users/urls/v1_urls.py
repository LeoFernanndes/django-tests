from django.urls import include, path
from rest_framework import routers

from users.views import v1_views


router = routers.DefaultRouter()
router.register(r'', v1_views.UserViewset, basename='users') 
router.register(f'/update-self', v1_views.UserUpdateSelf, basename='user-update-self')


urlpatterns = [
    path('users', include(router.urls)),
]

urlpatterns += router.urls
