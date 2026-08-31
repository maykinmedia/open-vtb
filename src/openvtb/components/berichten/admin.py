from django.contrib import admin

from .models import Bericht, BerichtType, Bijlage, BijlageType


class BijlageInline(admin.StackedInline):
    model = Bijlage
    extra = 0
    readonly_fields = ("uuid",)


@admin.register(Bericht)
class BerichtAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "onderwerp",
        "publicatiedatum",
        "ontvanger",
        "geopend_op",
        "is_gerelateerd_aan",
    )
    readonly_fields = ("uuid",)
    search_fields = ("uuid", "onderwerp")
    inlines = [BijlageInline]


class BijlageTypeInline(admin.StackedInline):
    model = BijlageType
    extra = 0
    readonly_fields = ("uuid",)


@admin.register(BerichtType)
class BerichtTypeAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "handelings_perspectief",
        "mijn_overheid_berichtenbox",
        "mijn_overheid_berichtenbox_type",
        "verantwoordelijke_organisatie",
    )
    readonly_fields = ("uuid",)
    search_fields = ("uuid", "handelings_perspectief")
    inlines = [BijlageTypeInline]
