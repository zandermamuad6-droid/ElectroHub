
from rest_framework import serializers

from components_app.models import Component
from .models import Inventory


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ["id", "name", "quantity", "price"]


class InventorySerializer(serializers.ModelSerializer):
    component_details = ComponentSerializer(
        source="component",
        read_only=True,
    )

    component_id = serializers.PrimaryKeyRelatedField(
        source="component",
        queryset=Component.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Inventory
        fields = [
            "id",
            "component_id",
            "component_details",
            "date_added",
        ]
        read_only_fields = ["id", "date_added"]
