
from django.urls import path

from .views import ComponentListCreateView, ComponentDetailView

urlpatterns = [
    path("", ComponentListCreateView.as_view(), name="component-list-create"),
    path("<int:pk>/", ComponentDetailView.as_view(), name="component-detail"),
]
