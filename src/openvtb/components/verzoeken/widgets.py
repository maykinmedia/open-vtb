import json

from jsonsuit.widgets import (
    JSONSuit as _JSONSuit,
    ReadonlyJSONSuit as _ReadonlyJSONSuit,
)


class JSONSuit(_JSONSuit):
    initial = dict()

    def get_schema(self):
        return {"type": "object", "properties": {}}

    def add_error(self, error_map):
        raise NotImplementedError("This method is not implemented")

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        try:
            json.loads(value)
        except ValueError:
            value = json.dumps(self.initial)
        return super().render(name, value, attrs)


class ReadonlyJSONSuit(_ReadonlyJSONSuit):
    def get_schema(self):
        return {"type": "object", "properties": {}}
