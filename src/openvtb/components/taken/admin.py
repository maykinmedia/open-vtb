from django.contrib import admin
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from openvtb.components.utils.widgets import JSONSuit

from .models import ExterneTaak


@admin.register(ExterneTaak)
class ExterneTaakdmin(admin.ModelAdmin):
    list_display = (
        "titel",
        "uuid",
        "taak_soort",
        "status",
        "startdatum",
    )
    readonly_fields = ("uuid",)
    list_filter = (
        "taak_soort",
        "status",
    )
    search_fields = (
        "uuid",
        "titel",
        "startdatum",
    )
    formfield_overrides = {
        JSONField: {
            "widget": JSONSuit,
            "error_messages": {
                "invalid": _("'%(value)s' value must be valid JSON"),
            },
        },
    }
