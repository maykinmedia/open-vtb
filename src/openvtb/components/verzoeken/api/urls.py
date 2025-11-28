from django.urls import include, path, re_path

from drf_spectacular.views import SpectacularRedocView
from vng_api_common import routers

from openvtb.components.verzoeken.api.viewsets import (
    VerzoekTypeVersionViewSet,
    VerzoekTypeViewSet,
    VerzoekViewSet,
)
from openvtb.utils.views import SpectacularJSONAPIView, SpectacularYAMLAPIView

from .schema import custom_settings

app_name = "verzoeken"

router = routers.DefaultRouter()
router.register("verzoeken", VerzoekViewSet)
router.register(
    "verzoektypen",
    VerzoekTypeViewSet,
    [routers.Nested("versions", VerzoekTypeVersionViewSet)],
)


urlpatterns = [
    re_path(
        r"^v(?P<version>\d+)/",
        include(
            [
                re_path(r"^", include(router.urls)),
                path(
                    "openapi.json",
                    SpectacularJSONAPIView.as_view(
                        urlconf="openvtb.components.verzoeken.api.urls",
                        custom_settings=custom_settings,
                    ),
                    name="schema-json-verzoeken",
                ),
                path(
                    "openapi.yaml",
                    SpectacularYAMLAPIView.as_view(
                        urlconf="openvtb.components.verzoeken.api.urls",
                        custom_settings=custom_settings,
                    ),
                    name="schema-yaml-verzoeken",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(
                        url_name="verzoeken:schema-yaml-verzoeken"
                    ),
                    name="schema-redoc-verzoeken",
                ),
            ]
        ),
    ),
]
