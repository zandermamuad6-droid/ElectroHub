
from rest_framework import generics, permissions

from .models import Inventory
from .serializers import InventorySerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow authenticated users to read inventory.
    Only staff users may create, update, or delete records.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class InventoryListCreateView(generics.ListCreateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return (
            Inventory.objects
            .select_related("component")
            .order_by("-date_added")
        )


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.select_related("component").all()
    serializer_class = InventorySerializer
    permission_classes = [IsAdminOrReadOnly]
