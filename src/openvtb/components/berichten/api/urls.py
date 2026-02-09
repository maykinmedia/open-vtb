from django.urls import include, path, re_path

from drf_spectacular.views import SpectacularRedocView
from vng_api_common import routers

from openvtb.utils.views import SpectacularJSONAPIView, SpectacularYAMLAPIView

from .schema import custom_settings
from .viewsets import BerichtViewset

app_name = "berichten"

router = routers.DefaultRouter()
router.register("berichten", BerichtViewset)


urlpatterns = [
    re_path(
        r"^v(?P<version>\d+)/",
        include(
            [
                re_path(r"^", include(router.urls)),
                path(
                    "openapi.json",
                    SpectacularJSONAPIView.as_view(
                        urlconf="openvtb.components.berichten.api.urls",
                        custom_settings=custom_settings,
                    ),
                    name="schema-json-berichten",
                ),
                path(
                    "openapi.yaml",
                    SpectacularYAMLAPIView.as_view(
                        urlconf="openvtb.components.berichten.api.urls",
                        custom_settings=custom_settings,
                    ),
                    name="schema-yaml-berichten",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(
                        url_name="berichten:schema-yaml-berichten"
                    ),
                    name="schema-redoc-berichten",
                ),
            ]
        ),
    ),
]
