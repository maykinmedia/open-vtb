from django.contrib.auth import get_user_model
from django.test import TestCase

from maykin_common.vcr import VCRMixin
from mozilla_django_oidc_db.tests.mixins import OIDCMixin
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from vng_api_common.tests import reverse

from openvtb.accounts.tests.factories import (
    OIDCClientFactory,
    TokenFactory,
    UserFactory,
)
from openvtb.components.berichten.tests.factories import BerichtFactory
from openvtb.utils.oidc_auth.constants import OIDC_API_CONFIG_IDENTIFIER
from openvtb.utils.oidc_auth.tests.utils import generate_token

User = get_user_model()


class TestApiOidcAuthentication(OIDCMixin, VCRMixin, TestCase):
    """
    Test results are stored in vc_cassettes dir

    To generate results, start the keycloak docker container located in open-vtb/docker
    & delete the files in vcr_cassettes
    """

    list_url = reverse("berichten:bericht-list")

    def setUp(self):
        super().setUp()
        self.bericht = BerichtFactory.create()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.oidc_client = OIDCClientFactory.create(
            with_keycloak_provider=True,
            with_admin=True,
            with_admin_options=True,
            oidc_rp_client_id="api-testid",
            oidc_rp_client_secret="y9qhit0CNdAyszI4q2qz35IahT000Nlp",
            identifier=OIDC_API_CONFIG_IDENTIFIER,
        )
        cls.oidc_client.options["user_settings"]["claim_mappings"]["username"] = ["sub"]
        cls.oidc_client.save()

    def test_valid_token_username_password(self):
        # create new user
        self.assertEqual(User.objects.all().count(), 0)
        payload = {
            "client_id": self.oidc_client.oidc_rp_client_id,
            "client_secret": self.oidc_client.oidc_rp_client_secret,
            "username": "testuser",
            "password": "testuser",
            "grant_type": "password",
            "scope": "openid",
        }
        token = generate_token(self.oidc_client, payload)
        response = self.client.get(
            self.list_url, headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_valid_token_oidc_create_user_false(self):
        # user already exists
        UserFactory.create(username="aa10cfc7-2c4d-41f6-8fac-7bf405c572c4")
        payload = {
            "client_id": self.oidc_client.oidc_rp_client_id,
            "client_secret": self.oidc_client.oidc_rp_client_secret,
            "username": "testuser",
            "password": "testuser",
            "grant_type": "password",
            "scope": "openid",
        }

        token = generate_token(self.oidc_client, payload)

        response = self.client.get(
            self.list_url, headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        # check only one user
        self.assertEqual(User.objects.all().count(), 1)

    def test_valid_client_credentials_token(self):
        self.assertEqual(User.objects.all().count(), 0)
        payload = {
            "client_id": self.oidc_client.oidc_rp_client_id,
            "client_secret": self.oidc_client.oidc_rp_client_secret,
            "grant_type": "client_credentials",
            "scope": "openid",
        }
        token = generate_token(self.oidc_client, payload)
        response = self.client.get(
            self.list_url, headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(User.objects.all().count(), 1)

    def test_invalid_token(self):
        self.assertEqual(User.objects.all().count(), 0)
        with self.subTest("invalid token string"):
            token = "test"
            response = self.client.get(
                self.list_url, headers={"Authorization": f"Bearer {token}"}
            )

            self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data["detail"], "Token verification failed")
            self.assertEqual(response.data["title"], "Ongeldige authenticatiegegevens.")
            self.assertEqual(response.data["code"], "authentication_failed")

            self.assertEqual(User.objects.all().count(), 0)

        with self.subTest("expired token"):
            expired_token = (
                "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0VU5RQWN2VWN2LURGVU94XzRPMWd0M"
                "TNPZEpTb3RxRUtQWnVyczJ2UVc4In0.eyJleHAiOjE3NDM1MTg5MzEsImlhdCI6MTc0MzUxODYzMSwian"
                "RpIjoiNTM0MmY0YWMtZWYzZi00YzE3LWEzZTItZDMzMWZmNGYyYmJiIiwiaXNzIjoiaHR0cDovL2xvY2F"
                "saG9zdDo4MDgwL3JlYWxtcy90ZXN0IiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImFhMTBjZmM3LTJjNGQt"
                "NDFmNi04ZmFjLTdiZjQwNWM1NzJjNCIsInR5cCI6IkJlYXJlciIsImF6cCI6InRlc3RpZCIsInNlc3Npb"
                "25fc3RhdGUiOiJlNmE0ZDU4ZC0yMzAzLTRhODUtODAyNC05ZmMzYTE2ZjI4MjAiLCJhY3IiOiIxIiwiYW"
                "xsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly8xMjcuMC4wLjE6ODAwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9"
                "sZXMiOlsiZGVmYXVsdC1yb2xlcy10ZXN0Iiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlv"
                "biJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiL"
                "CJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYW"
                "lsIHByb2ZpbGUga3ZrIGdyb3VwcyBic24iLCJzaWQiOiJlNmE0ZDU4ZC0yMzAzLTRhODUtODAyNC05ZmM"
                "zYTE2ZjI4MjAiLCJrdmsiOiIwMTIzNDU2NzgiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImxlZ2FsU3Vi"
                "amVjdElEIjoiMTIzNDU2NzgiLCJhY3RpbmdTdWJqZWN0SUQiOiI0Qjc1QTBFQTEwN0IzRDM2IiwibmFtZ"
                "V9xdWFsaWZpZXIiOiJ1cm46ZXRvZWdhbmc6MS45OkVudGl0eUNvbmNlcm5lZElEOkt2S25yIiwiZ3JvdX"
                "BzIjpbImRlZmF1bHQtcm9sZXMtdGVzdCIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24"
                "iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoidGVzdHVzZXIiLCJic24iOiIwMDAwMDAwMDAifQ.rlggtpiAr"
                "qtgrk9X4c9jkAS7l9bW4vLb0ujwDzSGfrUgOS5f7tnLukJzG-emDKIeEc4GkM1kYJB5KsE_v5Upioy3dQ"
                "7HDFwGtvfAF6Qtz5WsodPwMwp58a9XzyQXjUF5EI3EUS-g0QPkDV5T5duVCIaRnjQvSAZxxaPOAtG76Zz"
                "rPjJIBkfGsTgtZ6QwdbvbSooxUxcC4Eueq1FNgsw-Bk6LzgcYB8c_jiOR9tbYtzsLHX-88W6HG_AQ6hRb"
                "YfbWx0bIYx2a09bSWmYQxzx3N3O7Xw8ncwLLhtCXM8zIKmj6V0rpUGGPg0kHnocm-cfceyM1R42vwY54Z"
                "_955OCLfg"
            )
            response = self.client.get(
                self.list_url, headers={"Authorization": f"Bearer {expired_token}"}
            )

            self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data["detail"], "Token verification failed")
            self.assertEqual(response.data["title"], "Ongeldige authenticatiegegevens.")
            self.assertEqual(response.data["code"], "authentication_failed")

            self.assertEqual(User.objects.all().count(), 0)

        with self.subTest("no scope token"):
            payload = {
                "client_id": self.oidc_client.oidc_rp_client_id,
                "client_secret": self.oidc_client.oidc_rp_client_secret,
                "grant_type": "client_credentials",
            }

            token = generate_token(self.oidc_client, payload)
            response = self.client.get(
                self.list_url, headers={"Authorization": f"Bearer {token}"}
            )

            self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
            self.assertEqual(
                response.data["detail"],
                "OIDC authentication failed with status code: 403 www_authenticate: Missing openid scope",
            )
            self.assertEqual(response.data["title"], "Ongeldige authenticatiegegevens.")
            self.assertEqual(response.data["code"], "authentication_failed")

            self.assertEqual(User.objects.all().count(), 0)

    def test_invalid_oidc_not_configured(self):
        self.assertEqual(User.objects.all().count(), 0)
        self.oidc_client.oidc_provider = None
        self.oidc_client.save()

        token = "test"
        response = self.client.get(
            self.list_url, headers={"Authorization": f"Bearer {token}"}
        )

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"],
            "OIDC authentication failed: authentication is not properly configured.",
        )
        self.assertEqual(response.data["title"], "Ongeldige authenticatiegegevens.")
        self.assertEqual(response.data["code"], "authentication_failed")

        self.assertEqual(User.objects.all().count(), 0)

    def test_get(self):
        payload = {
            "client_id": self.oidc_client.oidc_rp_client_id,
            "client_secret": self.oidc_client.oidc_rp_client_secret,
            "username": "testuser",
            "password": "testuser",
            "grant_type": "password",
            "scope": "openid",
        }
        token = generate_token(self.oidc_client, payload)

        # get list
        response = self.client.get(
            self.list_url, headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        # get detail
        response = self.client.get(
            reverse(
                "berichten:bericht-detail", kwargs={"uuid": str(self.bericht.uuid)}
            ),
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(self.bericht.uuid))


class TestTokenAuthentication(TestCase):
    list_url = reverse("berichten:bericht-list")

    def setUp(self):
        super().setUp()
        self.bericht = BerichtFactory.create()

    def test_valid(self):
        token = TokenFactory.create()
        response = self.client.get(
            self.list_url,
            headers={"Authorization": f"Token {token}"},
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_invalid(self):
        with self.subTest("no token"):
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
            self.assertEqual(
                response.data["detail"], "Authenticatiegegevens zijn niet opgegeven."
            )
            self.assertEqual(
                response.data["title"], "Authenticatiegegevens zijn niet opgegeven."
            )
            self.assertEqual(response.data["code"], "not_authenticated")

        with self.subTest("invalid token"):
            token = "test"
            response = self.client.get(
                self.list_url,
                headers={"Authorization": f"Token {token}"},
            )
            self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data["detail"], "Ongeldige token.")
            self.assertEqual(response.data["title"], "Ongeldige authenticatiegegevens.")
            self.assertEqual(response.data["code"], "authentication_failed")

    def test_get(self):
        token = TokenFactory.create()

        # get list
        response = self.client.get(
            self.list_url, headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        # get detail
        response = self.client.get(
            reverse(
                "berichten:bericht-detail", kwargs={"uuid": str(self.bericht.uuid)}
            ),
            headers={"Authorization": f"Token {token}"},
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(self.bericht.uuid))
