from drf_spectacular.utils import inline_serializer


class SoortTaakMixinView:
    taak_soort: str = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.taak_soort is not None:
            qs = qs.filter(taak_soort=self.taak_soort)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.taak_soort is not None:
            context["taak_soort"] = self.taak_soort
        return context


def make_inline_response(
    name_suffix: str,
    parent_serializer_class,
    inner_serializer_class,
):
    parent_fields = {
        name: field
        for name, field in parent_serializer_class().fields.items()
        if name != "details"
    }
    parent_fields["details"] = inner_serializer_class()

    return inline_serializer(
        name=name_suffix,
        fields=parent_fields,
    )
