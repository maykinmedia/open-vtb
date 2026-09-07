from django.utils.translation import gettext_lazy as _

from django_filters import filters
from rest_framework.exceptions import ValidationError
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_help_text

from openvtb.utils.filters import URNFilter
from openvtb.utils.serializers import URNRelatedField

from ..models import Bericht, BerichtType


class BerichtFilter(FilterSet):
    bericht_type__uuid = filters.UUIDFilter(
        help_text=_("Zoek de Berichten op basis van de UUID van het BerichtType"),
        field_name="bericht_type__uuid",
    )
    bericht_type__urn = filters.CharFilter(
        help_text=_("Zoek berichten op basis van de exacte URN van het berichttype"),
        method="filter_bericht_type__urn",
    )
    geopend_op__isnull = filters.BooleanFilter(
        field_name="geopend_op",
        lookup_expr="isnull",
        help_text=_(
            "Filter op berichten die wel/niet geopend zijn. "
            "``true`` = nog niet geopend, ``false`` = wel geopend."
        ),
    )
    is_gerelateerd_aan = filters.CharFilter(
        method="filter_is_gerelateerd_aan",
        help_text=_(
            "Filter op URN aanwezig in de lijst isGerelateerdAan. Exacte match op de URN."
        ),
    )
    ontvanger = URNFilter(
        field_name="ontvanger",
        help_text=get_help_text("berichten.Bericht", "ontvanger"),
    )

    class Meta:
        model = Bericht
        fields = {
            "publicatiedatum": ["exact", "gt", "gte", "lt", "lte"],
        }

    def filter_bericht_type__urn(self, queryset, name, value):
        field = URNRelatedField(
            lookup_field="uuid",
            urn_resource="berichttype",
            queryset=BerichtType.objects.all(),
        )
        try:
            obj = field.to_internal_value(value)
        except Exception:
            raise ValidationError({"bericht_type__urn": _("Invalid or unknown URN.")})

        return queryset.filter(bericht_type=obj)

    def filter_is_gerelateerd_aan(self, queryset, name, value):
        return queryset.filter(is_gerelateerd_aan__contains=[{"urn": value}])


class BerichtTypeFilter(FilterSet):
    mijn_overheid_berichtenbox = filters.BooleanFilter(
        field_name="mijn_overheid_berichtenbox",
        help_text=_(
            "Filter op berichttypen die wel/niet geschikt zijn voor publicatie "
            "in de MijnOverheid Berichtenbox. "
            "``true`` = geschikt voor publicatie, ``false`` = niet geschikt voor publicatie."
        ),
    )
    verantwoordelijke_organisatie = URNFilter(
        field_name="verantwoordelijke_organisatie",
        help_text=get_help_text(
            "berichten.BerichtType", "verantwoordelijke_organisatie"
        ),
    )

    class Meta:
        model = BerichtType
        fields = {
            "uuid": ["exact"],
            "handelings_perspectief": ["exact"],
            "mijn_overheid_berichtenbox_type": ["exact"],
        }
