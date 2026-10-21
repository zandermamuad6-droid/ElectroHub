
from rest_framework import serializers

from .models import Component


class ComponentSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Component
        fields = [
            "id",
            "name",
            "quantity",
            "price",
            "image",
            "image_url",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        try:
            image_url = obj.image.url
        except (ValueError, OSError):
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(image_url)

        return image_url
