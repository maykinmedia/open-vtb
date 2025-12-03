import uuid

from rest_framework import serializers
from rest_framework.test import APITestCase

from openvtb.utils.serializers import URNRelatedField


class ModelVTB:
    def __init__(self, uuid):
        self.uuid = uuid


class QuerySetVTB:
    def __init__(self, objs, lookup_field):
        self.objs = objs
        self.lookup_field = lookup_field

    def get(self, **kwargs):
        key, value = list(kwargs.items())[0]
        for obj in self.objs:
            if str(getattr(obj, key)) == value:
                return obj
        return []


class SerializerVTB(serializers.Serializer):
    urn = URNRelatedField(
        view_name="vtb:test-detail",
        urn_component="vtb",
        urn_resource="test",
        lookup_field="uuid",
        read_only=True,
    )


class URNRelatedFieldTest(APITestCase):
    def setUp(self):
        self.fake_uuid = uuid.uuid4()
        self.obj = ModelVTB(uuid=uuid.uuid4())
        self.serializer = SerializerVTB(
            instance={"urn": self.obj}, context={"request": None}
        )

    def test_to_representation(self):
        field = self.serializer.fields["urn"]

        urn = field.to_representation(self.obj)

        self.assertTrue(urn.startswith("urn:maykin:vtb:test"))
        self.assertIn(str(self.obj.uuid), urn)

    def test_to_internal_value(self):
        field = self.serializer.fields["urn"]
        # mock get_queryset
        field.get_queryset = lambda: QuerySetVTB([self.obj], lookup_field="uuid")

        value = f"urn:maykin:test:{self.obj.uuid}"
        result = field.to_internal_value(value)

        self.assertEqual(result, self.obj)
