from django import forms
from django.contrib import admin, messages
from django.contrib.gis.db.models import GeometryField
from django.db.models import JSONField
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

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
from .widgets import JSONSuit


class BijlageTypeInline(admin.StackedInline):
    model = BijlageType
    extra = 0
    readonly_fields = ("uuid",)


class VerzoekTypeVersionInline(admin.StackedInline):
    model = VerzoekTypeVersion
    form = VerzoekTypeVersionForm
    verbose_name_plural = _("last version")
    extra = 0
    max_num = 1
    min_num = 1
    readonly_fields = ("version", "status", "published_at", "created_at", "modified_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        parent_id = request.resolver_match.kwargs.get("object_id")
        if not parent_id:
            return queryset
        last_version = (
            queryset.filter(verzoek_type_id=parent_id).order_by("-version").first()
        )
        if not last_version:
            return queryset.none()
        return queryset.filter(id=last_version.id)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VerzoekType)
class VerzoekTypeAdmin(admin.ModelAdmin):
    list_display = (
        "naam",
        "uuid",
        "opvolging",
        "created_at",
        "modified_at",
        "last_version",
    )
    search_fields = (
        "naam",
        "uuid",
    )
    inlines = [VerzoekTypeVersionInline, BijlageTypeInline]
    list_filter = ("opvolging",)
    readonly_fields = ("uuid",)

    def publish(self, request, obj):
        last_version = obj.last_version
        last_version.status = VerzoekTypeVersionStatus.PUBLISHED
        last_version.save()

        self.message_user(
            request,
            format_html(
                _("The VerzoekType {version} has been published successfully!"),
                version=obj.last_version,
            ),
            level=messages.SUCCESS,
        )

        return HttpResponseRedirect(request.path)

    def add_new_version(self, request, obj):
        new_version = obj.last_version
        new_version.pk = None
        new_version.version = new_version.version + 1
        new_version.status = VerzoekTypeVersionStatus.DRAFT
        new_version.save()

        self.message_user(
            request,
            format_html(
                _("The new version {version} has been created successfully!"),
                version=new_version,
            ),
            level=messages.SUCCESS,
        )

        return HttpResponseRedirect(request.path)

    def response_change(self, request, obj):
        if "_publish" in request.POST:
            return self.publish(request, obj)

        if "_newversion" in request.POST:
            return self.add_new_version(request, obj)

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
