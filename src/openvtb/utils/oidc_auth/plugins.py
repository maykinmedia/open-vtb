from mozilla_django_oidc_db.plugins import OIDCAdminPlugin
from mozilla_django_oidc_db.registry import register

from .constants import OIDC_API_CONFIG_IDENTIFIER


@register(OIDC_API_CONFIG_IDENTIFIER)
class OIDCApiPlugin(OIDCAdminPlugin):
    """
    This plugin must be registered to obtain a different
    ``OIDC_API_CONFIG_IDENTIFIER`` than the one used by ``OIDCAdminPlugin``.

    Inherits all properties and methods from OIDCAdminPlugin.
    Registration allows using a different OIDC configuration.
    """
