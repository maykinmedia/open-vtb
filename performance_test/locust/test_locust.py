"""
Load test for Open VTB: GET on every list endpoint, without filters.

At the end of the run the results are written in the Bencher Metric Format,
ready for `bencher run --adapter json`.
"""

import json
import logging
import os

from locust import HttpUser, between, events, task
from locust.runners import WorkerRunner

logger = logging.getLogger(__name__)

VERZOEKEN_LIST = "/verzoeken/api/v1/verzoeken"
TAKEN_LIST = "/taken/api/v1/externetaken"
BERICHTEN_LIST = "/berichten/api/v1/berichten"

AUTH_HEADERS = {
    "Authorization": f"Token {os.environ.get('OPENVTB_TOKEN', 'performance_token')}"
}
BMF_OUTPUT = os.environ.get("BMF_OUTPUT", "bencher_metric_format.json")

MS_TO_NS = 1_000_000


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    # Workers reset their stats after reporting them; only the master has the full picture.
    if isinstance(environment.runner, WorkerRunner):
        return
    write_bencher_metric_format(environment.stats, BMF_OUTPUT)


def _ns(value_ms) -> float:
    return (value_ms or 0) * MS_TO_NS


def _entry_metrics(entry) -> dict:
    """
    Metrics of one Locust stats entry, as Bencher measures.

    Latencies are in nanoseconds, like Bencher's built-in `latency` measure.
    """
    percentile = entry.get_response_time_percentile
    return {
        # Built-in measures
        "latency": {
            "value": _ns(percentile(0.95)),
            "lower_value": _ns(percentile(0.50)),
            "upper_value": _ns(percentile(0.99)),
        },
        "throughput": {"value": entry.total_rps},
        # Latency distribution (ns)
        "latency-mean": {"value": _ns(entry.avg_response_time)},
        "latency-min": {"value": _ns(entry.min_response_time)},
        "latency-max": {"value": _ns(entry.max_response_time)},
        "latency-p50": {"value": _ns(percentile(0.50))},
        "latency-p75": {"value": _ns(percentile(0.75))},
        "latency-p90": {"value": _ns(percentile(0.90))},
        "latency-p95": {"value": _ns(percentile(0.95))},
        "latency-p99": {"value": _ns(percentile(0.99))},
        "latency-p999": {"value": _ns(percentile(0.999))},
        # Volume and errors
        "requests": {"value": entry.num_requests},
        "failures": {"value": entry.num_failures},
        "failure-ratio": {"value": entry.fail_ratio},
        "failures-per-second": {"value": entry.total_fail_per_sec},
        # Payload (bytes)
        "response-size": {"value": entry.avg_content_length},
    }


def write_bencher_metric_format(stats, path: str) -> None:
    """
    Write the results in the Bencher Metric Format: one benchmark per task,
    plus an `aggregated` benchmark over all requests.
    """
    results = {}
    for (name, _method), entry in sorted(stats.entries.items()):
        if not entry.num_requests:
            continue
        results[name] = _entry_metrics(entry)

    results["aggregated"] = _entry_metrics(stats.total)

    with open(path, "w") as file:
        json.dump(results, file, indent=2)


class OpenVTBEndpoints(HttpUser):
    wait_time = between(1, 3)

    def _get_list(self, path: str, name: str) -> None:
        self.client.get(path, headers=AUTH_HEADERS, name=name)

    @task
    def get_verzoeken(self):
        self._get_list(VERZOEKEN_LIST, "verzoeken_list")

    @task
    def get_taken(self):
        self._get_list(TAKEN_LIST, "taken_list")

    @task
    def get_berichten(self):
        self._get_list(BERICHTEN_LIST, "berichten_list")
