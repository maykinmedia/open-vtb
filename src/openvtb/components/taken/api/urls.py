from django.urls import include, path, re_path

from drf_spectacular.views import SpectacularRedocView
from vng_api_common import routers

from openvtb.components.taken.api.viewsets import ExterneTaakViewSet
from openvtb.utils.views import SpectacularJSONAPIView, SpectacularYAMLAPIView

from .schema import custom_settings

app_name = "taken"

router = routers.DefaultRouter()
router.register("externetaken", ExterneTaakViewSet)


urlpatterns = [
    re_path(
        r"^v(?P<version>\d+)/",
        include(
            [
                re_path(r"^", include(router.urls)),
                path("", router.APIRootView.as_view(), name="api-root-taken"),
                path(
                    "openapi.json",
                    SpectacularJSONAPIView.as_view(
                        urlconf="openvtb.components.taken.api.urls",
                        custom_settings=custom_settings,
                    ),
                    name="schema-json-taken",
                ),
                path(
                    "openapi.yaml",
                    SpectacularYAMLAPIView.as_view(
                        urlconf="openvtb.components.taken.api.urls",
                        custom_settings=custom_settings,
                    ),
                    name="schema-yaml-taken",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(url_name="taken:schema-yaml-taken"),
                    name="schema-redoc-taken",
                ),
            ]
        ),
    ),
]
