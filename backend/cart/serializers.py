
from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
    )
    component_image = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "component",
            "component_name",
            "component_image",
            "price",
            "quantity",
            "subtotal",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "price",
            "component_name",
            "component_image",
            "subtotal",
            "created_at",
        ]

    def get_component_image(self, obj):
        image = obj.component.image

        if not image:
            return None

        try:
            image_url = image.url
        except (ValueError, OSError):
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(image_url)

        return image_url
