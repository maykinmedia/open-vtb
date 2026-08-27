import os

os.environ["_USE_STRUCTLOG"] = "True"
from celery.schedules import crontab
from maykin_common.branding import ProductDefinition
from maykin_common.config import (
    DocumentationParams,
    config,  # noqa
)
from maykin_common.health_checks import default_health_check_apps
from open_api_framework.conf.base import *  # noqa

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
    "django_celery_beat",
    # health check + plugins
    *default_health_check_apps,
    "maykin_common.health_checks.celery",
    # Project applications.
    "openvtb.accounts",
    "openvtb.utils",
    "openvtb.components.taken",
    "openvtb.components.verzoeken",
    "openvtb.components.berichten",
    # Django libraries
    "localflavor",
]

MIDDLEWARE += ["openvtb.utils.middleware.APIVersionHeaderMiddleware"]

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
#
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

#
# Geospatial libraries
#
GEOS_LIBRARY_PATH = config(
    "GEOS_LIBRARY_PATH",
    default=None,
    documentation=DocumentationParams(
        help_text=(
            "Full path to the GEOS library used by GeoDjango. In most circumstances, this can be left empty."
        ),
    ),
)
GDAL_LIBRARY_PATH = config(
    "GDAL_LIBRARY_PATH",
    default=None,
    documentation=DocumentationParams(
        help_text=(
            "Full path to the GDAL library used by GeoDjango. In most circumstances, this can be left empty."
        ),
    ),
)

#
# mozilla-django-oidc-db
#
OIDC_DRF_AUTH_BACKEND = "openvtb.utils.oidc_auth.oidc_backend.OIDCAuthenticationBackend"

#
# django-setup-configuration
#
SETUP_CONFIGURATION_STEPS = [
    "mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep",
    "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep",
    "notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep",
]

#
# notifications-api-common
#
NOTIFICATIONS_SOURCE = config(
    "NOTIFICATIONS_SOURCE",
    default="",
    documentation=DocumentationParams(
        help_text="The identifier of this application to use as the source in notifications and cloudevents",
    ),
)

LOG_NOTIFICATIONS_IN_DB = config(
    "LOG_NOTIFICATIONS_IN_DB",
    default=True,
    documentation=DocumentationParams(
        help_text="Indicates whether or not failed notifications/cloud events should be saved to the database"
    ),
)

NOTIFICATION_NUMBER_OF_DAYS_RETAINED = config(
    "NOTIFICATION_NUMBER_OF_DAYS_RETAINED",
    default=60,
    documentation=DocumentationParams(
        help_text="the number of days for which you wish to keep failed notifications/cloud events in the database"
    ),
)


#
# maykin-common
#
MKN_HEALTH_CHECKS_BEAT_LIVENESS_FILE = BASE_DIR / "tmp" / "celery_beat.live"
MKN_HEALTH_CHECKS_WORKER_EVENT_LOOP_LIVENESS_FILE = (
    BASE_DIR / "tmp" / "celery_worker_event_loop.live"
)
MKN_HEALTH_CHECKS_WORKER_READINESS_FILE = BASE_DIR / "tmp" / "celery_worker.ready"


#
# MAYKIN-COMMON branding
#
MKN_BRANDING_PRODUCT_DEFINITION = ProductDefinition(
    name="Open VTB",
    hyperlink="https://github.com/maykinmedia/open-vtb",
    logo_path="ico/open-vtb-icon.svg",
)

custom_product_name: str = config(
    "CUSTOM_PRODUCT_NAME",
    default="",
    documentation=DocumentationParams(
        help_text=(
            "Specify the custom product name when redistributing the application, e.g. "
            "as part of your own software suite."
        ),
        group="Branding",
    ),
)
custom_product_url: str = config(
    "CUSTOM_PRODUCT_URL",
    default="",
    documentation=DocumentationParams(
        help_text=(
            "Optional link for the custom product when redistributing the "
            "application. If provided, the product name will be clickable."
        ),
        group="Branding",
    ),
)
custom_product_logo_path: str = config(
    "CUSTOM_PRODUCT_LOGO_PATH",
    default="",
    documentation=DocumentationParams(group="Branding"),
)
custom_product_logo_url: str = config(
    "CUSTOM_PRODUCT_LOGO_URL",
    default="",
    documentation=DocumentationParams(
        help_text=(
            "Optional link for the custom product logo when redistributing the "
            "application. When using externally hosted assets, note that you may "
            "need to tweak the Content-Security-Policy settings."
        ),
        group="Branding",
    ),
)
MKN_BRANDING_DERIVED_PRODUCT_DEFINITION = (
    ProductDefinition(
        name=custom_product_name,
        hyperlink=custom_product_url,
        logo_path=custom_product_logo_path,
        logo_url=custom_product_logo_url,
    )
    if custom_product_name
    else None
)

# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#crontab-schedules
EVENTS_BERICHTEN_JOB_MINUTE = config(
    "EVENTS_BERICHTEN_JOB_MINUTE",
    default=0,
    documentation=DocumentationParams(
        help_text=(
            "Minute of execution (0 - 59) for the Berichten CloudEvents job. "
            "The job is triggered at this minute within each scheduled hour interval, "
            "as defined by the hour interval configuration. The schedule is evaluated in UTC timezone."
        ),
    ),
)

EVENTS_BERICHTEN_JOB_HOUR = config(
    "EVENTS_BERICHTEN_JOB_HOUR",
    default=1,
    documentation=DocumentationParams(
        help_text=(
            "Hour interval (1 - 23) for the Berichten CloudEvents job. Determines the frequency of execution in hours. "
            "The job runs repeatedly based on this interval rather than at a single fixed hour. "
            "Default is every hour. The schedule is evaluated in UTC timezone."
        ),
    ),
)

EVENTS_TAKEN_JOB_MINUTE = config(
    "EVENTS_TAKEN_JOB_MINUTE",
    default=0,
    documentation=DocumentationParams(
        help_text=(
            "Minute of execution (0 - 59) for the Taken CloudEvents job. "
            "The job is triggered at this minute within each scheduled hour interval, "
            "as defined by the hour interval configuration. The schedule is evaluated in UTC timezone."
        ),
    ),
)

EVENTS_TAKEN_JOB_HOUR = config(
    "EVENTS_TAKEN_JOB_HOUR",
    default=1,
    documentation=DocumentationParams(
        help_text=(
            "Hour interval (1 - 23) for the Taken CloudEvents job. Determines the frequency of execution in hours. "
            "The job runs repeatedly based on this interval rather than at a single fixed hour. "
            "Default is every hour. The schedule is evaluated in UTC timezone."
        ),
    ),
)

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "send-berichten-events": {
        "task": "openvtb.components.berichten.tasks.send_berichten_events",
        "schedule": crontab(
            minute=EVENTS_BERICHTEN_JOB_MINUTE,
            hour=f"*/{EVENTS_BERICHTEN_JOB_HOUR}",
        ),
    },
    "send-taken-events": {
        "task": "openvtb.components.taken.tasks.send_taak_events",
        "schedule": crontab(
            minute=EVENTS_TAKEN_JOB_MINUTE,
            hour=f"*/{EVENTS_TAKEN_JOB_HOUR}",
        ),
    },
}

####################
#                  #
# PROJECT SETTINGS #
#                  #
####################

#
# CloudEvents
#
ENABLE_CLOUD_EVENTS = config(
    "ENABLE_CLOUD_EVENTS",
    default=True,
    documentation=DocumentationParams(
        help_text="Indicates whether or not cloud events should be sent to the configured endpoint for specific operations via the API",
    ),
)

#
# URN settings
#
URN_NAMESPACE = config(
    "URN_NAMESPACE",
    documentation=DocumentationParams(
        help_text=("Namespace used in URNs schemas."),
    ),
)

TAKEN_DEFAULT_REMINDER_IN_DAYS = config(
    "TAKEN_DEFAULT_REMINDER_IN_DAYS",
    default=7,
    documentation=DocumentationParams(
        help_text=(
            "The default number of days before the `einddatumHandelingsTermijn` to send a reminder for a task. "
            "If ``0``, no reminders will be sent by default unless explicitly configured for a task."
        ),
    ),
)
