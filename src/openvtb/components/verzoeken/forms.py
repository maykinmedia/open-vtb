from django import forms

from .constants import VerzoekTypeVersionStatus
from .models import VerzoekTypeVersion
from .widgets import JSONSuit, ReadonlyJSONSuit


class VerzoekTypeVersionForm(forms.ModelForm):
    class Meta:
        model = VerzoekTypeVersion
        fields = ("aanvraag_gegevens_schema",)
        widgets = {
            "aanvraag_gegevens_schema": JSONSuit(),
        }

    def __init__(self, *args, **kwargs):
        json_field = "aanvraag_gegevens_schema"

        super().__init__(*args, **kwargs)
        if getattr(self.instance, "status", None) == VerzoekTypeVersionStatus.PUBLISHED:
            self.fields[json_field].widget = ReadonlyJSONSuit()
            self.fields[json_field].disabled = True
            self.fields[json_field].required = False
