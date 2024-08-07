from apps.api.views.base import BaseModelViewSet
from apps.gstream.models import *
from apps.api.serializers.colors import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class ColorsViewSet(BaseModelViewSet):
    queryset = ColorsConfig.objects.all()
    serializer_class = ColorsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
