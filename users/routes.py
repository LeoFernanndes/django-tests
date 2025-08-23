from rest_framework import routers

from users import views

# TODO: check why are raw string used to register routers


router = routers.DefaultRouter()
router.register(r'', views.UserViewset) 

urlpatterns = [

]

urlpatterns += router.urls
