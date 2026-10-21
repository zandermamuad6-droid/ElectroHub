
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from components_app.models import Component
from cart.models import CartItem, Order, OrderItem


User = get_user_model()


class CheckoutStockValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="checkout_test_user",
            password="TestPassword123!",
        )
        self.client.force_authenticate(user=self.user)

        self.component = Component.objects.create(
            name="Test Diode",
            quantity=5,
            price=Decimal("5.00"),
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            component=self.component,
            quantity=2,
            price=self.component.price,
        )

    def test_checkout_rejects_quantity_above_stock(self):
        CartItem.objects.filter(pk=self.cart_item.pk).update(
            quantity=6
        )

        response = self.client.post(
            "/api/cart/checkout/",
            {"payment_method": "cod"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.component.refresh_from_db()
        self.assertEqual(self.component.quantity, 5)
        self.assertFalse(
            Order.objects.filter(user=self.user).exists()
        )


class CartOwnershipTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.owner = User.objects.create_user(
            username="cart_owner",
            password="TestPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="other_cart_user",
            password="TestPassword123!",
        )

        self.component = Component.objects.create(
            name="Ownership Diode",
            quantity=20,
            price=Decimal("5.00"),
        )
        self.cart_item = CartItem.objects.create(
            user=self.owner,
            component=self.component,
            price=self.component.price,
            quantity=2,
        )

        self.client.force_authenticate(user=self.other_user)

    def test_user_cannot_retrieve_another_users_cart_item(self):
        response = self.client.get(
            f"/api/cart/{self.cart_item.pk}/"
        )
        self.assertEqual(response.status_code, 404)

    def test_user_cannot_update_another_users_cart_item(self):
        response = self.client.patch(
            f"/api/cart/{self.cart_item.pk}/",
            {"quantity": 3},
            format="json",
        )
        self.assertEqual(response.status_code, 404)

        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 2)

    def test_user_cannot_delete_another_users_cart_item(self):
        response = self.client.delete(
            f"/api/cart/{self.cart_item.pk}/"
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            CartItem.objects.filter(pk=self.cart_item.pk).exists()
        )


class SuccessfulCheckoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="checkout_success_user",
            password="TestPassword123!",
        )
        self.client.force_authenticate(user=self.user)

        self.component = Component.objects.create(
            name="Checkout Resistor",
            quantity=10,
            price=Decimal("12.50"),
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            component=self.component,
            price=self.component.price,
            quantity=3,
        )

    def test_checkout_creates_order_deducts_stock_and_clears_cart(self):
        response = self.client.post(
            "/api/cart/checkout/",
            {"payment_method": "cod"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["message"],
            "Order placed successfully.",
        )

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_amount, Decimal("37.50"))
        self.assertEqual(order.payment_method, "cod")
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.payment_status, "pending")
        self.assertTrue(order.order_number.startswith("EH-"))

        order_item = OrderItem.objects.get(order=order)
        self.assertEqual(order_item.component, self.component)
        self.assertEqual(order_item.component_name, "Checkout Resistor")
        self.assertEqual(order_item.price, Decimal("12.50"))
        self.assertEqual(order_item.quantity, 3)

        self.component.refresh_from_db()
        self.assertEqual(self.component.quantity, 7)
        self.assertFalse(
            CartItem.objects.filter(user=self.user).exists()
        )


class OrderOwnershipAndAdminPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            username="order_customer",
            password="TestPassword123!",
        )
        self.other_customer = User.objects.create_user(
            username="other_order_customer",
            password="TestPassword123!",
        )
        self.admin = User.objects.create_user(
            username="order_admin",
            password="TestPassword123!",
            is_staff=True,
        )

        self.component = Component.objects.create(
            name="Order Test Component",
            quantity=10,
            price=Decimal("8.00"),
        )

        self.customer_order = Order.objects.create(
            user=self.customer,
            order_number="EH-TESTCUSTOMER01",
            total_amount=Decimal("16.00"),
            status="pending",
            payment_method="cod",
            payment_status="pending",
        )
        OrderItem.objects.create(
            order=self.customer_order,
            component=self.component,
            component_name=self.component.name,
            price=Decimal("8.00"),
            quantity=2,
        )

        self.other_order = Order.objects.create(
            user=self.other_customer,
            order_number="EH-TESTOTHER0001",
            total_amount=Decimal("8.00"),
            status="pending",
            payment_method="cod",
            payment_status="pending",
        )

    def test_customer_only_sees_their_own_orders(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/cart/my-orders/")

        self.assertEqual(response.status_code, 200)
        returned_ids = {order["id"] for order in response.data}
        self.assertIn(self.customer_order.id, returned_ids)
        self.assertNotIn(self.other_order.id, returned_ids)

    def test_customer_cannot_access_admin_order_list(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/cart/admin-orders/")

        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_change_order_status(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            f"/api/cart/admin-orders/{self.customer_order.pk}/",
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        self.customer_order.refresh_from_db()
        self.assertEqual(self.customer_order.status, "pending")

    def test_staff_can_access_admin_order_list(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/cart/admin-orders/")

        self.assertEqual(response.status_code, 200)
        returned_ids = {order["id"] for order in response.data}
        self.assertIn(self.customer_order.id, returned_ids)
        self.assertIn(self.other_order.id, returned_ids)

    def test_staff_can_update_order_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/cart/admin-orders/{self.customer_order.pk}/",
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.customer_order.refresh_from_db()
        self.assertEqual(self.customer_order.status, "completed")
