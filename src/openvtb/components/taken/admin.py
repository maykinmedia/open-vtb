from django import forms
from django.contrib import admin

from .models import ExterneTaak


class ExterneTaakForm(forms.ModelForm):
    details = forms.JSONField(
        required=False,
        initial={},
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
    )

    class Meta:
        model = ExterneTaak
        fields = (
            "uuid",
            "titel",
            "status",
            "startdatum",
            "handelings_perspectief",
            "einddatum_handelings_termijn",
            "datum_herinnering",
            "toelichting",
            "is_toegewezen_aan_partij",
            "wordt_behandeld_door_medewerker",
            "hoort_bij_zaak",
            "heeft_betrekking_op_product",
            "taak_soort",
            "details",
        )


@admin.register(ExterneTaak)
class ExterneTaakdmin(admin.ModelAdmin):
    form = ExterneTaakForm
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
