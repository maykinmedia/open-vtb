"""
Generic Locust users for (paginated) DRF-style list endpoints.
"""

from collections.abc import Callable, Mapping
from typing import Any

import msgspec
from locust import HttpUser, between


class Page(msgspec.Struct):
    """A paginated DRF list. Other fields (count, next, previous) are ignored."""

    results: list[Any]


class ListEndpointsTest(HttpUser):
    """GET list endpoints and check they return a non-empty list."""

    abstract = True

    wait_time = between(1, 3)
    headers: Mapping[str, str] = {}
    response_type: type = Page

    def get_list(self, path: str, name: str) -> None:
        with self.client.get(
            path, headers=self.headers, name=name, catch_response=True
        ) as response:
            # Non-2xx responses are failures already.
            if response.status_code != 200:
                return
            try:
                body = msgspec.json.decode(response.content, type=self.response_type)
            except msgspec.ValidationError as exc:
                response.failure(f"Unexpected response shape: {exc}")
                return
            except msgspec.DecodeError:
                response.failure("Invalid JSON")
                return

            items = body.results if isinstance(body, Page) else body
            if not items:
                response.failure("Empty list")


def list_tasks(
    endpoints: Mapping[str, str], params: str = ""
) -> list[Callable[[ListEndpointsTest], None]]:
    """
    One task per endpoint, all with the same weight.

    ``endpoints`` maps the request name (the benchmark name on Bencher) to its path.
    """

    def make_task(name: str, path: str) -> Callable[[ListEndpointsTest], None]:
        url = f"{path}?{params}" if params else path

        def task(user: ListEndpointsTest) -> None:
            user.get_list(url, name)

        task.__name__ = f"get_{name}"
        return task

    return [make_task(name, path) for name, path in endpoints.items()]
