from rest_framework.test import APITestCase as APITestCaseDRF

from openvtb.accounts.tests.factories import TokenFactory


class APITestCase(APITestCaseDRF):
    def setUp(self):
        super().setUp()
        self.token_auth = TokenFactory.create()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_auth.key)
