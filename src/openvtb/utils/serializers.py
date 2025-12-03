import re
import sys
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import fields as drf_fields, serializers
from rest_framework.relations import (
    ObjectTypeError,
    ObjectValueError,
    RelatedField,
)
from rest_framework.serializers import Serializer
from rest_framework.utils.field_mapping import (
    get_nested_relation_kwargs,
    get_url_kwargs,
)


def get_from_serializer_data_or_instance(
    field: str, data: dict, serializer: Serializer
) -> Any:
    serializer_field = serializer.fields[field]
    data_value = data.get(serializer_field.source, drf_fields.empty)
    if data_value is not drf_fields.empty:
        return data_value

    instance = serializer.instance
    if not instance:
        return None

    return serializer_field.get_attribute(instance)


class NoUrnMatch(Exception):
    pass


class URNRelatedField(RelatedField):
    """
    A DRF field for representing related objects as URNs.

    URN format: urn:<component>:<resource>:<lookup_value>

    - urn_namespace: required or derived from the settings default
    - urn_component: derived from the view
    - urn_resource: derived from the related model name
    - lookup_value: value used to lookup the object (e.g., UUID or pk)

    """

    URN_PATTERN = re.compile(r"^urn:([^:]+):([^:]+):(.+)$")
    UUID_REGEX = (
        "([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"
    )

    lookup_field = "pk"
    view_name = None

    urn_namespace = None
    urn_component = None
    urn_resource = None

    default_error_messages = {
        "required": _("This field is required."),
        "no_match": _("Invalid URN - Could not match the expected pattern."),
        "incorrect_match": _("Invalid URN - Does not conform to the expected format."),
        "does_not_exist": _("Invalid URN - Corresponding object does not exist."),
        "incorrect_type": _(
            "Incorrect type. Expected a string representing a URN, received {data_type}."
        ),
    }

    def __init__(self, view_name=None, urn_namespace=None, **kwargs):
        self.view_name = view_name
        if urn_namespace is None:
            self.urn_namespace = settings.URN_NAMESPACE
        assert self.urn_namespace is not None, (
            "The `urn_namespace` argument is required."
        )

        self.lookup_field = kwargs.pop("lookup_field", self.lookup_field)
        self.urn_component = kwargs.pop("urn_component", self.urn_component)
        self.urn_resource = kwargs.pop("urn_resource", self.urn_resource)

        super().__init__(**kwargs)

    def get_object(self, value):
        """
        Return the object corresponding to a matched URN.
        """
        lookup_kwargs = {self.lookup_field: value}
        queryset = self.get_queryset()
        try:
            return queryset.get(**lookup_kwargs)
        except ValueError:
            exc = ObjectValueError(str(sys.exc_info()[1]))
            raise exc.with_traceback(sys.exc_info()[2])
        except TypeError:
            exc = ObjectTypeError(str(sys.exc_info()[1]))
            raise exc.with_traceback(sys.exc_info()[2])

    def get_urn_resource(self):
        """
        Extract the `urn_resource` name from the model associated with the view.
        """
        try:
            return self.context["view"].queryset.model._meta.model_name
        except Exception:
            raise ImproperlyConfigured(
                "URNRelatedField could not determine the `urn_resource`: "
                "model not found on the view or serializer."
            )

    def get_urn_component(self):
        """
        Extract the `urn_component` name from the DRF request context.
        """
        try:
            return self.context["request"].resolver_match.namespace
        except (KeyError, AttributeError, ValueError):
            raise ImproperlyConfigured(
                "URNRelatedField could not determine the `urn_component`: "
                "request, resolver_match, or namespace is missing in serializer context."
            )

    def get_urn(self, obj):
        """
        Given an object, return the URN that links to the object.
        """

        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        if self.urn_component is None:
            self.urn_component = self.get_urn_component()

        assert self.urn_component, (
            "URNRelatedField requires a `urn_component` to be specified."
        )

        if self.urn_resource is None:
            self.urn_resource = self.get_urn_resource()

        assert self.urn_resource, (
            "URNRelatedField requires a `urn_resource` to be specified."
        )

        value = getattr(obj, self.lookup_field)
        return (
            f"urn:{self.urn_namespace}:{self.urn_component}:{self.urn_resource}:{value}"
        )

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("incorrect_type", data_type=type(data).__name__)

        if not data.startswith("urn:"):
            self.fail("no_match")

        match = self.URN_PATTERN.match(data)
        if not match:
            self.fail("incorrect_match")

        urn_component, urn_resource, urn_identifier = match.groups()

        lookup_value = urn_identifier
        if self.lookup_field == "uuid":
            if not re.match(self.UUID_REGEX, lookup_value):
                self.fail("incorrect_match")

        try:
            return self.get_object(lookup_value)
        except (ObjectDoesNotExist, ObjectValueError, ObjectTypeError):
            self.fail("does_not_exist")

    def to_representation(self, value):
        try:
            return self.get_urn(value)
        except NoUrnMatch:
            raise ImproperlyConfigured(
                "Could not resolve URN for the object using the configured view. "
                "You may have failed to include the related model in your API, "
                "or incorrectly configured the `urn_component` or `urn_resource` for this field."
            )


@extend_schema_field(OpenApiTypes.STR)
class URNIdentityField(URNRelatedField):
    """
    A read-only field that exposes the object's URN identity.
    """

    def __init__(self, view_name=None, **kwargs):
        assert view_name is not None, "The `view_name` argument is required."
        kwargs["read_only"] = True
        kwargs["source"] = "*"
        super().__init__(view_name, **kwargs)

    def use_pk_only_optimization(self):
        return False


class UrnModelSerializer(serializers.ModelSerializer):
    serializer_related_field = URNIdentityField
    urn_field_name = "urn"

    def get_default_field_names(self, declared_fields, model_info):
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return (
            [self.urn_field_name]
            + list(declared_fields)
            + list(model_info.fields)
            + list(model_info.forward_relations)
        )

    def build_urn_field(self, field_name, model_class):
        """
        Constructs a URNRelatedField for the given model class.
        """
        field_class = self.serializer_related_field
        field_kwargs = get_url_kwargs(model_class)
        return field_class, field_kwargs

    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Overrides the default field building to insert URN fields where appropriate.
        """
        if field_name == self.urn_field_name:
            return self.build_urn_field(field_name, model_class)
        return super().build_field(field_name, info, model_class, nested_depth)

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """

        class NestedSerializer(UrnModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = "__all__"

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
