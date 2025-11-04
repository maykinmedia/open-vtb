from vng_api_common.conf.api import *  # noqa - imports white-listed

# Remove the reference - we don't have a single API version.
del API_VERSION  # noqa

VERZOEK_API_VERSION = "0.0.1"
TAKEN_API_VERSION = "0.0.1"
BERICHTEN_API_VERSION = "0.0.1"


REST_FRAMEWORK = BASE_REST_FRAMEWORK.copy()
REST_FRAMEWORK["PAGE_SIZE"] = 100
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = (
    "vng_api_common.pagination.DynamicPageSizePagination"
)
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework.authentication.TokenAuthentication",
)

VNG_COMPONENTS_BRANCH = "master"
