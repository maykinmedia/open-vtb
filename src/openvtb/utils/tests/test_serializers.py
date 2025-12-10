import uuid

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.test import override_settings

from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from openvtb.utils.serializers import URNRelatedField


class ModelVTB:
    def __init__(self, uuid):
        self.uuid = uuid


class QuerySetVTB:
    def __init__(self, objects, lookup_field):
        self.objects = objects
        self.lookup_field = lookup_field

    def get(self, **kwargs):
        key, value = list(kwargs.items())[0]
        for obj in self.objects:
            if str(getattr(obj, key)) == value:
                return obj
        raise ObjectDoesNotExist()


class SerializerVTB(serializers.Serializer):
    urn = URNRelatedField(
        view_name="vtb:test-detail",
        urn_component="vtb",
        urn_resource="test",
        lookup_field="uuid",
        required=True,
        queryset=QuerySetVTB([], lookup_field="uuid"),
    )


class URNRelatedFieldTest(APITestCase):
    def setUp(self):
        self.fake_uuid = uuid.uuid4()
        self.object = ModelVTB(uuid=uuid.uuid4())
        self.serializer = SerializerVTB(instance=self.object, context={"request": None})

    def test_to_representation(self):
        field = self.serializer.fields["urn"]

        urn = field.to_representation(self.object)

        self.assertEqual(urn, f"urn:maykin:vtb:test:{str(self.object.uuid)}")

    def test_to_internal_value(self):
        field = self.serializer.fields["urn"]
        field.get_queryset = lambda: QuerySetVTB([self.object], lookup_field="uuid")

        value = f"urn:maykin:test:{self.object.uuid}"
        result = field.to_internal_value(value)

        self.assertEqual(result, self.object)

    def test_validation(self):
        with self.subTest("test required"):
            serializer = SerializerVTB(context={"request": None}, data={})
            serializer.is_valid()
            self.assertEqual(
                serializer.errors,
                {
                    "urn": [
                        ErrorDetail(
                            string="Dit veld is vereist.",
                            code="required",
                        )
                    ],
                },
            )

        with self.subTest("test no_match"):
            serializer = SerializerVTB(context={"request": None}, data={"urn": "test"})
            serializer.is_valid()
            self.assertEqual(
                serializer.errors,
                {
                    "urn": [
                        ErrorDetail(
                            string="Invalid URN - Could not match the expected pattern.",
                            code="no_match",
                        )
                    ]
                },
            )

        with self.subTest("test incorrect_match"):
            serializer = SerializerVTB(context={"request": None}, data={"urn": "urn:"})
            serializer.is_valid()
            self.assertEqual(
                serializer.errors,
                {
                    "urn": [
                        ErrorDetail(
                            string="Invalid URN - Does not conform to the expected format.",
                            code="incorrect_match",
                        )
                    ]
                },
            )

        with self.subTest("test incorrect_match uuid"):
            serializer = SerializerVTB(
                context={"request": None}, data={"urn": "urn:test:test:1234"}
            )
            serializer.is_valid()
            self.assertEqual(
                serializer.errors,
                {
                    "urn": [
                        ErrorDetail(
                            string="Invalid URN - Does not conform to the expected format.",
                            code="incorrect_match",
                        )
                    ]
                },
            )

        with self.subTest("test incorrect_type"):
            serializer = SerializerVTB(context={"request": None}, data={"urn": []})
            serializer.is_valid()
            self.assertEqual(
                serializer.errors,
                {
                    "urn": [
                        ErrorDetail(
                            string="Incorrect type. Expected a string representing a URN, received list.",
                            code="incorrect_type",
                        )
                    ]
                },
            )

        with self.subTest("test does_not_exist"):
            serializer = SerializerVTB(
                context={"request": None}, data={"urn": f"urn:test:test:{uuid.uuid4()}"}
            )
            serializer.is_valid()
            self.assertEqual(
                serializer.errors,
                {
                    "urn": [
                        ErrorDetail(
                            string="Invalid URN - Corresponding object does not exist.",
                            code="does_not_exist",
                        )
                    ]
                },
            )

    def test_invalid_configuration(self):
        with self.subTest("test urn_component is None"):
            field = self.serializer.fields["urn"]

            # urn_component is None
            field.urn_component = None
            # request is None
            self.assertIsNone(self.serializer.context["request"])

            with self.assertRaises(ImproperlyConfigured) as error:
                field.to_representation(self.object)

            self.assertEqual(
                str(error.exception),
                "URNRelatedField could not determine the `urn_component`:"
                " request, resolver_match, or namespace is missing in serializer context.",
            )

            field.urn_component = "vtb"

        with self.subTest("test urn_resource is None"):
            field = self.serializer.fields["urn"]

            # urn_resource is None
            field.urn_resource = None
            # request is None
            self.assertIsNone(self.serializer.context["request"])

            with self.assertRaises(ImproperlyConfigured) as error:
                field.to_representation(self.object)

            self.assertEqual(
                str(error.exception),
                "URNRelatedField could not determine the `urn_resource`: "
                "model not found on the view or serializer.",
            )

            field.urn_resource = "test"

        with self.subTest("test no urn match"):
            field = self.serializer.fields["urn"]

            with self.assertRaises(ImproperlyConfigured) as error:
                new_object = ModelVTB(uuid=None)
                field.to_representation(new_object)

            self.assertEqual(
                str(error.exception),
                "Could not resolve URN for the object using the configured view."
                " You may have failed to include the related model in your API, or"
                " incorrectly configured the `urn_component` or `urn_resource` for this field.",
            )

    @override_settings(URN_NAMESPACE="")
    def test_empty_urn_namespace(self):
        self.assertEqual(settings.URN_NAMESPACE, "")

        with self.assertRaises(ImproperlyConfigured) as error:
            field = self.serializer.fields["urn"]
            field.to_representation(self.object)

        self.assertEqual(
            str(error.exception),
            "URNRelatedField requires a `urn_namespace` to be specified.",
        )
