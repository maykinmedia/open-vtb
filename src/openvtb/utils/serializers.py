from typing import Any

from rest_framework.serializers import Serializer


def get_field_value(
    serializer: Serializer, attrs: dict[str, Any], field_name: str
) -> Any:
    """
    Helper function to retrieve a field value from either the attrs (new data)
    or the instance (existing data during updates).

    :param serializer: The serializer instance
    :param attrs: The attributes passed to `.validate`
    :param field_name: The name of the field to retrieve
    :return: The value of the field, or None if not present
    """
    if field_name in attrs:
        return attrs.get(field_name)
    # Fallback to instance value if it exists
    if serializer.instance:
        return getattr(serializer.instance, field_name, None)
    return None
