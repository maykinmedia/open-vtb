from django.contrib.auth import authenticate, get_user_model
from django.test import RequestFactory, TestCase

from .factories import UserFactory

User = get_user_model()


class LoginTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory.create(username="admin", password="admin")

    def test_login_success(self):
        request = self.factory.post("/admin/login/")
        user = authenticate(request=request, username="admin", password="admin")

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")

    def test_login_success_email(self):
        request = self.factory.post("/admin/login/")
        self.user.email = "admin@example.com"
        self.user.save()

        user = authenticate(
            request=request, username="admin@example.com", password="admin"
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "admin")

    def test_login_fails_with_unknown_user(self):
        request = self.factory.post("/admin/login/")
        user = authenticate(request=request, username="foo", password="bar")

        self.assertIsNone(user)

    def test_login_fails_with_wrong_password(self):
        request = self.factory.post("/admin/login/")
        user = authenticate(request=request, username="admin", password="wrong")

        self.assertIsNone(user)
