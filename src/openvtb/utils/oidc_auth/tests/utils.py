import requests
from mozilla_django_oidc_db.models import OIDCClient, OIDCProvider


def generate_token(client: OIDCClient, payload: dict) -> str:
    """
    Generate an access token using the payload data
    """
    assert isinstance(client.oidc_provider, OIDCProvider)
    response = requests.post(client.oidc_provider.oidc_op_token_endpoint, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]
