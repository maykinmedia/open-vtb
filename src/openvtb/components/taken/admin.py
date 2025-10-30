from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import ExterneTaak


class ExterneTaakForm(forms.ModelForm):
    data = forms.JSONField(
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
            "taak_soort",
            "data",
        )

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        taak_soort = cleaned_data.get("taak_soort")
        if data and not taak_soort:
            raise ValidationError(
                {
                    "taak_soort": _(
                        "Dit veld is verplicht voordat u het veld 'data' kunt instellen"
                    )
                }
            )
        return cleaned_data


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
