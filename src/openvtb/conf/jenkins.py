# ruff: noqa: F403,F405
import os
import warnings

os.environ.setdefault("DEBUG", "no")
os.environ.setdefault("SECRET_KEY", "for-testing-purposes-only")
os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("ALLOWED_HOSTS", "")

os.environ.setdefault("DB_USER", "jenkins")
os.environ.setdefault("DB_PASSWORD", "jenkins")
# PostgreSQL 9.6: 5432 (default for Jenkins)
os.environ.setdefault("DB_PORT", "5432")

os.environ.setdefault("ENVIRONMENT", "jenkins")

from .base import *  # noqa isort:skip


def get_db_name(prefix):
    """
    get a reasonable name below Postgres' 63 char name limit
    """
    job = os.getenv("JOB_NAME", default="").lower().rsplit("/", 1)[-1]
    build = os.getenv("BUILD_NUMBER", default="0")
    lim = 63 - 2 - len(prefix) - len(build)
    return f"{prefix}_{job[:lim]}_{build}"


DATABASES["default"]["TEST"] = {"NAME": get_db_name("test_openvtb")}

LOGGING["loggers"].update(
    {
        "django": {
            "handlers": ["django"],
            "level": "WARNING",
            "propagate": True,
        },
    }
)

#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = (
    False  # Required to allow FakeRequest and the like to work correctly.
)

# in memory cache and django-axes don't get along.
# https://django-axes.readthedocs.io/en/latest/configuration.html#known-configuration-problems
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "axes": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

ELASTIC_APM["DEBUG"] = True

# disable 2 FA in tests
MAYKIN_2FA_ALLOW_MFA_BYPASS_BACKENDS = AUTHENTICATION_BACKENDS

# THOU SHALT NOT USE NAIVE DATETIMES
warnings.filterwarnings(
    "error",
    r"DateTimeField .* received a naive datetime",
    RuntimeWarning,
    r"django\.db\.models\.fields",
)
