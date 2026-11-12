"""
Generic Locust users for (paginated) DRF-style list endpoints.
"""

from collections.abc import Callable, Mapping

from locust import HttpUser, between


class ListEndpointsTest(HttpUser):
    """GET list endpoints and check they return a non-empty list."""

    abstract = True

    wait_time = between(1, 3)
    headers: Mapping[str, str] = {}
    results_key = "results"

    def get_list(self, path: str, name: str) -> None:
        with self.client.get(
            path, headers=self.headers, name=name, catch_response=True
        ) as response:
            # Non-2xx responses are failures already.
            if response.status_code != 200:
                return
            try:
                results = response.json().get(self.results_key)
            except ValueError:
                response.failure("Invalid JSON")
                return
            if not results:
                response.failure("Empty response")


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
