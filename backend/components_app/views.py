
from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from .models import Component
from .serializers import ComponentSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access to authenticated users.
    Only staff users may create, update, or delete components.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class ComponentListCreateView(generics.ListCreateAPIView):
    queryset = Component.objects.all().order_by("name")
    serializer_class = ComponentSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class ComponentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
