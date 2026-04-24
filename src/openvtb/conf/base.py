import os

os.environ["_USE_STRUCTLOG"] = "True"
from celery.schedules import crontab
from maykin_common.health_checks import default_health_check_apps
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

#
# URN settings
#
URN_NAMESPACE = config(
    "URN_NAMESPACE",
    help_text=("Namespace used in URNs schemas."),
)

#
# MOZILLA DJANGO OIDC
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


TAKEN_DEFAULT_REMINDER_IN_DAYS = config(
    "TAKEN_DEFAULT_REMINDER_IN_DAYS",
    default=7,
    help_text=(
        "The default number of days before the `einddatumHandelingsTermijn` to send a reminder for a task. "
        "If ``0``, no reminders will be sent by default unless explicitly configured for a task."
    ),
)

ENABLE_CLOUD_EVENTS = config(
    "ENABLE_CLOUD_EVENTS",
    default=True,
    cast=bool,
    help_text="Indicates whether or not cloud events should be sent to the configured endpoint for specific operations via the API",
)

NOTIFICATIONS_SOURCE = config(
    "NOTIFICATIONS_SOURCE",
    default="",
    help_text="The identifier of this application to use as the source in notifications and cloudevents",
)


#
# CELERY-ONCE
#
CELERY_ONCE_REDIS_URL = config(
    "CELERY_ONCE_REDIS_URL",
    default=CELERY_BROKER_URL,
    group="Celery",
)
CELERY_ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {
        "url": CELERY_ONCE_REDIS_URL,
        "default_timeout": 60 * 60,  # one hour
    },
}

# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#crontab-schedules
PUBLISHED_BERICHTEN_JOB_MINUTE = config(
    "PUBLISHED_BERICHTEN_JOB_MINUTE",
    default=0,
    help_text=(
        "Minute of execution (0 - 59). The job is triggered at this minute within each scheduled hour interval, "
        "as defined by the hour interval configuration. The schedule is evaluated in UTC timezone."
    ),
)

PUBLISHED_BERICHTEN_JOB_HOUR = config(
    "PUBLISHED_BERICHTEN_JOB_HOUR",
    default=1,
    help_text=(
        "Hour interval (1 - 23). Determines the frequency of execution in hours. "
        "The job runs repeatedly based on this interval rather than at a single fixed hour. "
        "Default is every hour. The schedule is evaluated in UTC timezone."
    ),
)

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "send-published-berichten": {
        "task": "openvtb.components.berichten.tasks.send_published_berichten",
        "schedule": crontab(
            minute=PUBLISHED_BERICHTEN_JOB_MINUTE,
            hour=f"*/{PUBLISHED_BERICHTEN_JOB_HOUR}",
        ),
    },
}


#
# MAYKIN-COMMON health checks
#
MKN_HEALTH_CHECKS_BEAT_LIVENESS_FILE = BASE_DIR / "tmp" / "celery_beat.live"
MKN_HEALTH_CHECKS_WORKER_EVENT_LOOP_LIVENESS_FILE = (
    BASE_DIR / "tmp" / "celery_worker_event_loop.live"
)
MKN_HEALTH_CHECKS_WORKER_READINESS_FILE = BASE_DIR / "tmp" / "celery_worker.ready"
