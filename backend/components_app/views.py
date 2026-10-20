
from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from .models import Component
from .serializers import ComponentSerializer


class ComponentListCreateView(generics.ListCreateAPIView):
    queryset = Component.objects.all().order_by("name")
    serializer_class = ComponentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class ComponentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
