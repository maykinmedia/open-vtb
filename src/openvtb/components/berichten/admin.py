from django.contrib import admin

from .models import Bericht, Bijlage


class BijlageInline(admin.StackedInline):
    model = Bijlage
    extra = 0
    readonly_fields = ("uuid",)


@admin.register(Bericht)
class BerichtAdmin(admin.ModelAdmin):
    list_display = ("uuid", "onderwerp", "publicatiedatum", "ontvanger", "geopend_op")
    readonly_fields = ("uuid",)
    search_fields = ("uuid", "onderwerp")
    inlines = [BijlageInline]
