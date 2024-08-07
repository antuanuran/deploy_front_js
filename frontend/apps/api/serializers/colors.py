from apps.gstream.models import *
from apps.api.serializers.base import BaseModelSerializer


class ColorsSerializer(BaseModelSerializer):
    class Meta:
        model = ColorsConfig
        fields = ["color_name", "path"]
