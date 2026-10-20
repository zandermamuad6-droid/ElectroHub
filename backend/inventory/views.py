
from rest_framework import generics, permissions

from .models import Inventory
from .serializers import InventorySerializer


class InventoryListCreateView(generics.ListCreateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Inventory.objects
            .select_related("component")
            .order_by("-date_added")
        )


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.select_related("component").all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
