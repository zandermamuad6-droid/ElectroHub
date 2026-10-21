
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from components_app.models import Component
from inventory.models import Inventory


User = get_user_model()


class InventoryPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            username="inventory_customer",
            password="SecurePass123!",
        )
        self.admin = User.objects.create_user(
            username="inventory_admin",
            password="SecurePass123!",
            is_staff=True,
        )

        self.component = Component.objects.create(
            name="Inventory Test Component",
            quantity=20,
            price=Decimal("15.00"),
        )

        self.inventory = Inventory.objects.create(
            component=self.component,
            quantity=12,
            minimum_stock=5,
        )

        self.list_url = "/api/inventory/"
        self.detail_url = f"/api/inventory/{self.inventory.pk}/"

    def test_unauthenticated_user_cannot_list_inventory(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    def test_customer_can_list_inventory(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_customer_can_retrieve_inventory(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)

    def test_customer_cannot_create_inventory(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.list_url,
            {"component_id": self.component.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Inventory.objects.count(), 1)

    def test_customer_cannot_update_inventory(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            self.detail_url,
            {"component_id": self.component.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_customer_cannot_delete_inventory(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Inventory.objects.filter(
                pk=self.inventory.pk
            ).exists()
        )

    def test_admin_can_create_inventory(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_url,
            {"component_id": self.component.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Inventory.objects.count(), 2)

    def test_admin_can_update_inventory(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_url,
            {"component_id": self.component.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_can_delete_inventory(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Inventory.objects.filter(
                pk=self.inventory.pk
            ).exists()
        )
