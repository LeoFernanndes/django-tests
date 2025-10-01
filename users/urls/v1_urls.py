from django.urls import include, path
from rest_framework import routers

from users.views import v1_views


router = routers.DefaultRouter()
router.register(r'', v1_views.UserViewset, basename='users') 


urlpatterns = [
    path('users/', include(router.urls)),
    path('users/generate-upload-profile-image-presigned-url', v1_views.UserImageUploadView.as_view(), name='generate-upload-profile-image-presigned-url')
]

