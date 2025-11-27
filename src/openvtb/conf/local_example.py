#
# Any machine specific settings when using development settings.
#

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "openvtb",
        "USER": "openvtb",
        "PASSWORD": "openvtb",
        # Empty for localhost through domain sockets or '127.0.0.1' for localhost
        # through TCP.
        "HOST": "",
        "PORT": "",  # Set to empty string for default.
    }
}
