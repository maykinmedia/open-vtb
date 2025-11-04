from django.utils.translation import gettext_lazy as _

from drf_spectacular.openapi import (
    AutoSchema as _AutoSchema,
)
from drf_spectacular.utils import OpenApiParameter
from vng_api_common.constants import VERSION_HEADER


class AutoSchema(_AutoSchema):
    def get_response_serializers(
        self,
    ):
        if self.method == "DELETE":
            return {204: None}

        return super().get_response_serializers()

    def get_override_parameters(self):
        """Add request GEO headers"""
        params = super().get_override_parameters()
        version_headers = self.get_version_headers()

        return params + version_headers

    def get_version_headers(self) -> list[OpenApiParameter]:
        return [
            OpenApiParameter(
                name=VERSION_HEADER,
                type=str,
                location=OpenApiParameter.HEADER,
                description=_(
                    "Geeft een specifieke API-versie aan in de context van "
                    "een specifieke aanroep. Voorbeeld: 1.2.1."
                ),
                response=True,
            )
        ]
