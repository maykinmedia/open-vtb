from django.contrib import admin

from .models import Bericht, BerichtOntvanger, Bijlage


class BijlageInline(admin.StackedInline):
    model = Bijlage
    extra = 0
    readonly_fields = ("uuid",)


@admin.register(Bericht)
class BerichtAdmin(admin.ModelAdmin):
    list_display = ("uuid", "onderwerp", "publicatiedatum")
    readonly_fields = ("uuid",)
    search_fields = ("uuid", "onderwerp")
    inlines = [BijlageInline]


@admin.register(BerichtOntvanger)
class BerichtOntvangerAdmin(admin.ModelAdmin):
    list_display = ("uuid", "geadresseerde", "geopend_op", "geopend")
    readonly_fields = ("uuid",)
    search_fields = ("uuid", "geadresseerde", "geopend_op")
    list_filter = ("geopend",)
