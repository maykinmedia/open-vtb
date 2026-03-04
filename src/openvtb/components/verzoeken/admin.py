from django import forms
from django.contrib import admin, messages
from django.contrib.gis.db.models import GeometryField
from django.db.models import JSONField
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from openvtb.components.utils.widgets import JSONSuit

from .constants import VerzoekTypeVersionStatus
from .forms import VerzoekTypeVersionForm
from .models import (
    Bijlage,
    BijlageType,
    Verzoek,
    VerzoekBetaling,
    VerzoekBron,
    VerzoekType,
    VerzoekTypeVersion,
)


@admin.register(BijlageType)
class BijlageTypeAdmin(admin.ModelAdmin):
    model = BijlageType
    readonly_fields = ("uuid",)


class VerzoekTypeVersionInline(admin.StackedInline):
    model = VerzoekTypeVersion
    form = VerzoekTypeVersionForm
    verbose_name_plural = _("last versie")
    extra = 0
    max_num = 1
    min_num = 1

    readonly_fields = (
        "versie",
        "status",
        "begin_geldigheid",
        "aangemaakt_op",
        "gewijzigd_op",
        "einde_geldigheid",
        "bijlage_typen_list",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        parent_id = request.resolver_match.kwargs.get("object_id")
        if not parent_id:
            return queryset
        last_versie = (
            queryset.filter(verzoek_type_id=parent_id).order_by("-versie").first()
        )
        if not last_versie:
            return queryset.none()
        return queryset.filter(id=last_versie.id)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VerzoekType)
class VerzoekTypeAdmin(admin.ModelAdmin):
    list_display = (
        "naam",
        "uuid",
        "aangemaakt_op",
        "gewijzigd_op",
        "last_versie",
    )
    search_fields = (
        "naam",
        "uuid",
    )
    inlines = [VerzoekTypeVersionInline]
    readonly_fields = ("uuid",)

    def publish(self, request, obj):
        last_versie = obj.last_versie
        last_versie.status = VerzoekTypeVersionStatus.PUBLISHED
        last_versie.save()

        self.message_user(
            request,
            format_html(
                _("The VerzoekType {versie} has been published successfully!"),
                versie=obj.last_versie,
            ),
            level=messages.SUCCESS,
        )

        return HttpResponseRedirect(request.path)

    def add_new_versie(self, request, obj):
        new_versie = obj.last_versie
        new_versie.pk = None
        new_versie.versie = new_versie.versie + 1
        new_versie.status = VerzoekTypeVersionStatus.DRAFT
        new_versie.save()

        self.message_user(
            request,
            format_html(
                _("The new versie {versie} has been created successfully!"),
                versie=new_versie,
            ),
            level=messages.SUCCESS,
        )

        return HttpResponseRedirect(request.path)

    def response_change(self, request, obj):
        if "_publish" in request.POST:
            return self.publish(request, obj)

        if "_newversie" in request.POST:
            return self.add_new_versie(request, obj)

        return super().response_change(request, obj)


class VerzoekBetalingInline(admin.StackedInline):
    model = VerzoekBetaling
    extra = 0
    max_num = 1


class VerzoekBronInline(admin.StackedInline):
    model = VerzoekBron
    extra = 0
    max_num = 1


class BijlageInline(admin.StackedInline):
    model = Bijlage
    extra = 0
    readonly_fields = ("uuid",)


@admin.register(Verzoek)
class VerzoekAdmin(admin.ModelAdmin):
    list_display = ("uuid", "verzoek_type")
    readonly_fields = ("uuid",)
    search_fields = ("uuid", "verzoek_type__naam", "bron__naam")
    inlines = [VerzoekBronInline, VerzoekBetalingInline, BijlageInline]
    list_filter = ("verzoek_type",)
    formfield_overrides = {
        GeometryField: {"widget": forms.Textarea},
        JSONField: {
            "widget": JSONSuit,
            "error_messages": {
                "invalid": _("'%(value)s' value must be valid JSON"),
            },
        },
    }
