from django.utils.translation import gettext_lazy as _

from django_filters import filters
from rest_framework.exceptions import ValidationError
from vng_api_common.filtersets import FilterSet

from openvtb.utils.filters import ListURNFilter, URNFilter
from openvtb.utils.serializers import URNRelatedField

from ..models import Verzoek, VerzoekType


class VerzoekFilter(FilterSet):
    verzoek_type__uuid = filters.UUIDFilter(
        help_text=_("Zoek de Verzoeken op basis van de UUID van het VerzoekType"),
        field_name="verzoek_type__uuid",
    )
    verzoek_type__urn = filters.CharFilter(
        help_text=_("Zoek de Verzoeken op basis van de URN van het VerzoekType"),
        method="filter_verzoek_type__urn",
    )
    is_gerelateerd_aan = ListURNFilter(
        field_name="is_gerelateerd_aan",
        help_text=_(
            "Filter op URN aanwezig in de lijst isGerelateerdAan. "
            "Exacte match op een volledig URN-segment (gescheiden door `:`)."
        ),
    )
    verzoek_betaling__transactie_referentie = filters.CharFilter(
        method="filter_verzoek_betaling_transactiereferentie",
    )
    verzoek_betaling__voltooid = filters.BooleanFilter(
        method="filter_verzoek_betaling_voltooid",
    )
    initiator = URNFilter(
        field_name="initiator",
        help_text=_(
            "Filtert op een exacte match van een volledig segment van de URN "
            "(gescheiden door `:`) in het veld `initiator`."
        ),
    )
    mede_initiator = URNFilter(
        field_name="mede_initiator",
        help_text=_(
            "Filtert op een exacte match van een volledig segment van de URN "
            "(gescheiden door `:`) in het veld `mede_initiator`."
        ),
    )
    verzoek_informatie_object = URNFilter(
        field_name="verzoek_informatie_object",
        help_text=_(
            "Filtert op een exacte match van een volledig segment van de URN "
            "(gescheiden door `:`) in het veld `verzoek_informatie_object`."
        ),
    )

    class Meta:
        model = Verzoek
        fields = {
            "uuid": ["exact"],
            "versie": ["exact"],
            "verwerk_status": ["exact"],
        }

    def filter_verzoek_type__urn(self, queryset, name, value):
        field = URNRelatedField(
            lookup_field="uuid",
            urn_resource="verzoektype",
            queryset=VerzoekType.objects.all(),
        )
        try:
            obj = field.to_internal_value(value)
        except Exception:
            raise ValidationError({"verzoek_type__urn": _("Invalid or unknown URN.")})

        return queryset.filter(verzoek_type=obj)

    def filter_verzoek_betaling_transactiereferentie(self, queryset, name, value):
        return queryset.filter(betaling__transactie_referentie=value)

    def filter_verzoek_betaling_voltooid(self, queryset, name, value):
        return queryset.filter(betaling__voltooid=value)


class VerzoekTypeFilter(FilterSet):
    class Meta:
        model = VerzoekType
        fields = {
            "uuid": ["exact"],
            "naam": ["exact"],
            "omschrijving": ["icontains"],
        }
