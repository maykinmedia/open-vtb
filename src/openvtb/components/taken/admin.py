from django.contrib import admin

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

    list_filter = (
        "taak_soort",
        "status",
    )
    search_fields = (
        "uuid",
        "titel",
        "startdatum",
    )
