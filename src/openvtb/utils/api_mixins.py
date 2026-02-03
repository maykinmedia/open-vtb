from djangorestframework_camel_case.util import camel_to_underscore


class CamelToUnderscoreMixin:
    def to_representation(self, instance):
        instance = {camel_to_underscore(k): v for k, v in instance.items()}
        return super().to_representation(instance)
