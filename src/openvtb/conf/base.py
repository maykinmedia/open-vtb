import os

os.environ["_USE_STRUCTLOG"] = "True"

from open_api_framework.conf.base import *  # noqa
from open_api_framework.conf.utils import config  # noqa

from .api import *  # noqa

#
# APPLICATIONS enabled for this project
#
INSTALLED_APPS = INSTALLED_APPS + [
    "capture_tag",
    "maykin_common",
    "rest_framework.authtoken",
    "django.contrib.gis",
    # External applications.
    "jsonsuit.apps.JSONSuitConfig",
    # Project applications.
    "openvtb.accounts",
    "openvtb.utils",
    "openvtb.components.taken",
    "openvtb.components.verzoeken",
    # Django libraries
    "localflavor",
]


#
# SECURITY settings
#
CSRF_FAILURE_VIEW = "maykin_common.views.csrf_failure"

# This setting is used by the csrf_failure view (accounts app).
# You can specify any path that should match the request.path
# Note: the LOGIN_URL Django setting is not used because you could have
# multiple login urls defined.
LOGIN_URLS = [reverse_lazy("admin:login")]

#
# Custom settings
#
PROJECT_NAME = "Open VTB"
SITE_TITLE = "API dashboard"

# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

##############################
#                            #
# 3RD PARTY LIBRARY SETTINGS #
#                            #
##############################

#
# Django-Admin-Index
#
ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS = True
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "maykin_common.django_two_factor_auth.should_display_dropdown_menu"
)

#
# Define this variable here to ensure it shows up in the envvar documentation
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# Geospatial libraries
GEOS_LIBRARY_PATH = config(
    "GEOS_LIBRARY_PATH",
    None,
    help_text=(
        "Full path to the GEOS library used by GeoDjango. In most circumstances, this can be left empty."
    ),
)
GDAL_LIBRARY_PATH = config(
    "GDAL_LIBRARY_PATH",
    None,
    help_text=(
        "Full path to the GDAL library used by GeoDjango. In most circumstances, this can be left empty."
    ),
)

# URN settings
URN_NAMESPACE = config(
    "URN_NAMESPACE", None, help_text=("Namespace used in URNs schemas.")
)
