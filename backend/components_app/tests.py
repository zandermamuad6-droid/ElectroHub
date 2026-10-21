
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from components_app.models import Component


User = get_user_model()


class ComponentPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            username="component_customer",
            password="SecurePass123!",
        )
        self.admin = User.objects.create_user(
            username="component_admin",
            password="SecurePass123!",
            is_staff=True,
        )

        self.component = Component.objects.create(
            name="Permission Test Component",
            quantity=10,
            price=Decimal("25.00"),
        )

        self.list_url = "/api/components/"
        self.detail_url = f"/api/components/{self.component.pk}/"

    def test_unauthenticated_user_cannot_list_components(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    def test_customer_can_list_components(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

    def test_customer_can_retrieve_component(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)

    def test_customer_cannot_create_component(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.list_url,
            {
                "name": "Unauthorized Component",
                "quantity": 5,
                "price": "10.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Component.objects.filter(
                name="Unauthorized Component"
            ).exists()
        )

    def test_customer_cannot_update_component(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            self.detail_url,
            {"name": "Modified Component"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        self.component.refresh_from_db()
        self.assertEqual(
            self.component.name,
            "Permission Test Component",
        )

    def test_customer_cannot_delete_component(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Component.objects.filter(
                pk=self.component.pk
            ).exists()
        )

    def test_admin_can_create_component(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.list_url,
            {
                "name": "Admin Created Component",
                "quantity": 5,
                "price": "10.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Component.objects.filter(
                name="Admin Created Component"
            ).exists()
        )

    def test_admin_can_update_component(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_url,
            {"name": "Admin Updated Component"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.component.refresh_from_db()
        self.assertEqual(
            self.component.name,
            "Admin Updated Component",
        )

    def test_admin_can_delete_component(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Component.objects.filter(
                pk=self.component.pk
            ).exists()
        )
