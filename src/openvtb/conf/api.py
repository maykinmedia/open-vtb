from vng_api_common.conf.api import *  # noqa - imports white-listed

# Remove the reference - we don't have a single API version.
del API_VERSION  # noqa

VERZOEK_API_VERSION = "0.1.0"
TAKEN_API_VERSION = "0.1.0"
BERICHTEN_API_VERSION = "0.1.0"


REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 100

# content of these fields must not be converted to camelCase
REST_FRAMEWORK["JSON_UNDERSCOREIZE"] = {
    "no_underscore_before_number": False,
    "ignore_fields": (
        "ontvangen_gegevens",
        "formulier_definitie",
        "aanvraag_gegevens",
        "aanvraag_gegevens_schema",
    ),
    "ignore_keys": None,
}
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = (
    "vng_api_common.pagination.DynamicPageSizePagination"
)
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "openvtb.utils.oidc_drf_middleware.OIDCAuthentication",
    "rest_framework.authentication.TokenAuthentication",
)
REST_FRAMEWORK["AUTHENTICATION_WHITELIST"] = [
    "openvtb.utils.oidc_drf_middleware.OIDCAuthentication",
    "rest_framework.authentication.TokenAuthentication",
]
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "openvtb.utils.schema.AutoSchema"

SPECTACULAR_SETTINGS = {
    "REDOC_DIST": "SIDECAR",
    "SERVE_INCLUDE_SCHEMA": False,
    "CAMELIZE_NAMES": True,
    "SCHEMA_PATH_PREFIX": r"/v[0-9]+",
    "SCHEMA_PATH_PREFIX_TRIM": True,
    "ENUM_GENERATE_CHOICE_DESCRIPTION": False,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
        "maykin_common.drf_spectacular.hooks.remove_invalid_url_defaults",
    ],
    "CONTACT": {
        "email": "standaarden.ondersteuning@vng.nl",
        "name": "VNG",
        "url": "https://zaakgerichtwerken.vng.cloud",
    },
    "LICENSE": {
        "name": "EUPL 1.2",
        "url": "https://opensource.org/licenses/EUPL-1.2",
    },
}

VNG_COMPONENTS_BRANCH = "master"
