import structlog
from drf_spectacular.utils import inline_serializer

from openvtb.utils.cloudevents import process_cloudevent

from ..constants import EXTERNETAAK_GEREGISTREERD

logger = structlog.stdlib.get_logger(__name__)


class SoortTaakMixin:
    taak_soort: str = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.taak_soort:
            qs = qs.filter(taak_soort=self.taak_soort)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.taak_soort:
            context["taak_soort"] = self.taak_soort
        return context

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        if self.taak_soort:
            logger.info("externetaak_created", uuid=str(instance.uuid))
        else:
            logger.info(f"{self.taak_soort}_created", uuid=str(instance.uuid))  # noqa

        process_cloudevent(
            type_event=EXTERNETAAK_GEREGISTREERD,
            subject=str(instance.uuid),
            data={
                "taak_soort": instance.taak_soort,
                "titel": instance.titel,
                "status": instance.status,
                "einddatumHandelingsTermijn": instance.einddatum_handelings_termijn.isoformat(),
            },
        )


def make_inline_response(
    name_suffix: str,
    parent_serializer_class,
    inner_serializer_class,
    write: bool = False,
):
    parent_fields = {
        name: field
        for name, field in parent_serializer_class().fields.items()
        if name != "details"
    }

    # remove taak_soort in write mode
    if write and "taak_soort" in parent_fields:
        parent_fields.pop("taak_soort")

    parent_fields["details"] = inner_serializer_class()

    return inline_serializer(
        name=name_suffix,
        fields=parent_fields,
    )
