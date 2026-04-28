import structlog
from drf_spectacular.utils import inline_serializer

from ..cloudevents import (
    EXTERNETAAK_AFGEBROKEN,
    EXTERNETAAK_GEREGISTREERD,
    EXTERNETAAK_UITGEVOERD,
    EXTERNETAAK_VERWERKT,
    send_taak_cloudevent,
)
from ..constants import StatusTaak

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

        logger.info(
            "externetaak_created",
            uuid=str(instance.uuid),
            taak_soort=self.taak_soort,
        )
        send_taak_cloudevent(EXTERNETAAK_GEREGISTREERD, instance)

    def perform_update(self, serializer):
        old_instance = self.get_object()
        super().perform_update(serializer)
        updated_instance = serializer.instance
        logger.info("externetaak_updated", uuid=str(updated_instance.uuid))

        old_status = old_instance.status
        new_status = updated_instance.status

        if old_status == new_status:
            return

        match new_status:
            case StatusTaak.UITGEVOERD:
                send_taak_cloudevent(EXTERNETAAK_UITGEVOERD, updated_instance)
            case StatusTaak.VERWERKT:
                send_taak_cloudevent(EXTERNETAAK_VERWERKT, updated_instance)
            case StatusTaak.AFGEBROKEN:
                send_taak_cloudevent(EXTERNETAAK_AFGEBROKEN, updated_instance)


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
