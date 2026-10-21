
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.logout_url = "/api/auth/logout/"
        self.me_url = "/api/auth/me/"
        self.csrf_url = "/api/auth/csrf/"

        self.user = User.objects.create_user(
            username="auth_test_user",
            email="auth_test@example.com",
            password="SecurePass123!",
        )

    def test_csrf_endpoint_is_public(self):
        response = self.client.get(self.csrf_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfToken", response.data)

    def test_registration_creates_customer_with_hashed_password(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "new_customer",
                "email": "new_customer@example.com",
                "display_name": "New Customer",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="new_customer")
        self.assertTrue(user.check_password("SecurePass123!"))
        self.assertNotEqual(user.password, "SecurePass123!")
        self.assertEqual(user.role, "customer")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registration_rejects_short_password(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "short_password_user",
                "email": "short@example.com",
                "display_name": "Short Password",
                "password": "short",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(
                username="short_password_user"
            ).exists()
        )

    def test_registration_rejects_duplicate_username_case_insensitively(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "AUTH_TEST_USER",
                "email": "different@example.com",
                "display_name": "Duplicate Username",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "another_user",
                "email": "AUTH_TEST@example.com",
                "display_name": "Duplicate Email",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_rejects_missing_credentials(self):
        response = self.client.post(
            self.login_url,
            {"username": "auth_test_user"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "auth_test_user",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_establishes_session_and_me_returns_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "auth_test_user",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["user"]["username"],
            "auth_test_user",
        )

        me_response = self.client.get(self.me_url)

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(
            me_response.data["username"],
            "auth_test_user",
        )

    def test_me_rejects_unauthenticated_user(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, 403)

    def test_logout_ends_authenticated_session(self):
        login_response = self.client.post(
            self.login_url,
            {
                "username": "auth_test_user",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)

        logout_response = self.client.post(self.logout_url)

        self.assertEqual(logout_response.status_code, 200)

        me_response = self.client.get(self.me_url)

        self.assertEqual(me_response.status_code, 403)
