
from django.urls import path

from .views import (
    CartListCreateView,
    CartItemDetailView,
    CheckoutView,
    MyOrdersView,
    AdminOrdersView,
    AdminOrderStatusView,
)

urlpatterns = [
    path("", CartListCreateView.as_view(), name="cart-list-create"),
    path("checkout/", CheckoutView.as_view(), name="cart-checkout"),
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("admin-orders/", AdminOrdersView.as_view(), name="admin-orders"),
    path(
        "admin-orders/<int:pk>/",
        AdminOrderStatusView.as_view(),
        name="admin-order-status",
    ),
    path("<int:pk>/", CartItemDetailView.as_view(), name="cart-item-detail"),
]
