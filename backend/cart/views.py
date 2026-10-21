
import uuid
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from components_app.models import Component
from .models import CartItem, Order, OrderItem
from .serializers import CartItemSerializer




class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            user=self.request.user
        ).select_related("component")

    def create(self, request, *args, **kwargs):
        component_id = request.data.get("component")
        raw_quantity = request.data.get("quantity", 1)

        try:
            if isinstance(raw_quantity, bool):
                raise ValueError

            quantity = int(raw_quantity)

            if quantity < 1 or str(quantity) != str(raw_quantity).strip():
                raise ValueError

        except (TypeError, ValueError):
            return Response(
                {"quantity": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            component = Component.objects.get(pk=component_id)
        except (Component.DoesNotExist, TypeError, ValueError):
            return Response(
                {"component": "Component not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if quantity > component.quantity:
            return Response(
                {"quantity": "Requested quantity exceeds available stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            component=component,
            defaults={
                "price": component.price,
                "quantity": quantity,
            },
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > component.quantity:
                return Response(
                    {"quantity": "Requested quantity exceeds available stock."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.quantity = new_quantity
            cart_item.price = component.price
            cart_item.save()

        response_status = (
            status.HTTP_201_CREATED if created
            else status.HTTP_200_OK
        )

        return Response(
            self.get_serializer(cart_item).data,
            status=response_status,
        )


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return CartItem.objects.filter(
            user=self.request.user
        ).select_related("component")

    def partial_update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        raw_quantity = request.data.get("quantity")

        try:
            if isinstance(raw_quantity, bool):
                raise ValueError

            quantity = int(raw_quantity)

            if quantity < 1 or str(quantity) != str(raw_quantity).strip():
                raise ValueError

        except (TypeError, ValueError):
            return Response(
                {"quantity": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        component = cart_item.component

        if quantity > component.quantity:
            return Response(
                {"quantity": "Requested quantity exceeds available stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity
        cart_item.price = component.price
        cart_item.save()

        return Response(
            self.get_serializer(cart_item).data,
            status=status.HTTP_200_OK,
        )


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        payment_method = request.data.get("payment_method", "cod")

        if payment_method != "cod":
            return Response(
                {"payment_method": "Only Cash on Delivery is supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                cart_items = list(
                    CartItem.objects.filter(user=request.user)
                    .select_related("component")
                    .order_by("component_id")
                )

                if not cart_items:
                    return Response(
                        {"detail": "Your cart is empty."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                component_ids = sorted({
                    item.component_id for item in cart_items
                })

                locked_components = {
                    component.pk: component
                    for component in (
                        Component.objects.select_for_update()
                        .filter(pk__in=component_ids)
                        .order_by("pk")
                    )
                }

                total_amount = Decimal("0.00")
                order_lines = []

                for item in cart_items:
                    component = locked_components.get(item.component_id)

                    if component is None:
                        raise ValueError(
                            f"Component {item.component_id} no longer exists."
                        )

                    if item.quantity < 1:
                        raise ValueError(
                            f"Invalid quantity for {component.name}."
                        )

                    if component.quantity < item.quantity:
                        raise ValueError(
                            f"Not enough stock for {component.name}. "
                            f"Available: {component.quantity}; "
                            f"requested: {item.quantity}."
                        )

                    current_price = component.price
                    total_amount += current_price * item.quantity

                    order_lines.append({
                        "component": component,
                        "component_name": component.name,
                        "price": current_price,
                        "quantity": item.quantity,
                    })

                order = Order.objects.create(
                    user=request.user,
                    order_number=f"EH-{uuid.uuid4().hex[:12].upper()}",
                    total_amount=total_amount,
                    status="pending",
                    payment_method="cod",
                    payment_status="pending",
                )

                for line in order_lines:
                    OrderItem.objects.create(
                        order=order,
                        component=line["component"],
                        component_name=line["component_name"],
                        price=line["price"],
                        quantity=line["quantity"],
                    )

                    line["component"].quantity -= line["quantity"]
                    line["component"].save(update_fields=["quantity"])

                CartItem.objects.filter(user=request.user).delete()

                response_data = {
                    "message": "Order placed successfully.",
                    "order": {
                        "id": order.id,
                        "order_number": order.order_number,
                        "total_amount": str(order.total_amount),
                        "status": order.status,
                        "payment_method": order.payment_method,
                        "payment_status": order.payment_status,
                        "created_at": order.created_at.isoformat(),
                        "items": [
                            {
                                "component_name": line["component_name"],
                                "price": str(line["price"]),
                                "quantity": line["quantity"],
                                "subtotal": str(
                                    line["price"] * line["quantity"]
                                ),
                            }
                            for line in order_lines
                        ],
                    },
                }

            return Response(
                response_data,
                status=status.HTTP_201_CREATED,
            )

        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MyOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).order_by("-created_at")

        orders_data = []

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)

            items_data = [
                {
                    "component_name": item.component_name,
                    "price": str(item.price),
                    "quantity": item.quantity,
                    "subtotal": str(item.subtotal),
                }
                for item in order_items
            ]

            orders_data.append({
                "id": order.id,
                "order_number": order.order_number,
                "total_amount": str(order.total_amount),
                "status": order.status,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "created_at": order.created_at.isoformat(),
                "items": items_data,
            })

        return Response(
            orders_data,
            status=status.HTTP_200_OK,
        )

class IsAdminUser(permissions.BasePermission):
    """
    Only authenticated staff users can access admin order endpoints.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class AdminOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = (
            Order.objects
            .select_related("user")
            .order_by("-created_at")
        )

        data = []

        for order in orders:
            order_items = OrderItem.objects.filter(order=order)

            items_data = [
                {
                    "component_name": item.component_name,
                    "price": str(item.price),
                    "quantity": item.quantity,
                    "subtotal": str(item.subtotal),
                }
                for item in order_items
            ]

            data.append({
                "id": order.id,
                "order_number": order.order_number,
                "customer": (
                    order.user.get_full_name()
                    or order.user.get_username()
                ),
                "customer_id": order.user_id,
                "total_amount": str(order.total_amount),
                "status": order.status,
                "payment_method": order.payment_method,
                "payment_status": order.payment_status,
                "created_at": order.created_at.isoformat(),
                "items": items_data,
            })

        return Response(data, status=status.HTTP_200_OK)


class AdminOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.data.get("status")

        # Validate against the actual choices defined in the model.
        status_choices = order._meta.get_field("status").choices
        allowed_statuses = {
            choice[0] for choice in status_choices
        }

        if new_status not in allowed_statuses:
            return Response(
                {
                    "error": "Invalid order status.",
                    "allowed_statuses": sorted(allowed_statuses),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save(update_fields=["status"])

        return Response(
            {
                "message": "Order status updated successfully.",
                "order_number": order.order_number,
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )
