from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.api.views.colors import *

router = DefaultRouter()
router.register("colors", ColorsViewSet)


urlpatterns = [
    path("auth/", include("djoser.urls.jwt")),
    path("", include("djoser.urls")),

    path("", include(router.urls)),

]
