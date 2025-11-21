from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

verzoektype_uuid_param = OpenApiParameter(
    name="verzoektype_uuid",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    required=True,
    description=_("UUID van het VerzoekType"),
)
