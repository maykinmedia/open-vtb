"""
Report Locust results to Bencher, in the Bencher Metric Format (BMF).
"""

import json
import os
import tempfile

from locust import events
from locust.runners import WorkerRunner

BMF_FILENAME = "bencher_metric_format.json"


def _default_bmf_output() -> str:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        directory = os.environ["RUNNER_TEMP"]
    else:
        directory = tempfile.gettempdir()
    return os.path.join(directory, BMF_FILENAME)


BMF_OUTPUT = os.environ.get("BMF_OUTPUT") or _default_bmf_output()
MS_TO_NS = 1_000_000


def _ns(value_ms) -> float:
    return (value_ms or 0) * MS_TO_NS


def entry_metrics(entry) -> dict:
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
        # Volume
        "requests": {"value": entry.num_requests},
        # Payload (bytes)
        "response-size": {"value": entry.avg_content_length},
    }


def write_bencher_metric_format(stats, path: str) -> None:
    """
    Write the results in the Bencher Metric Format: one benchmark per request
    name, plus an `aggregated` benchmark over all requests.

    No file is written without results.
    """
    results = {}
    for (name, _method), entry in sorted(stats.entries.items()):
        if not entry.num_requests:
            continue
        results[name] = entry_metrics(entry)

    if not results:
        return

    results["aggregated"] = entry_metrics(stats.total)

    with open(path, "w") as file:
        json.dump(results, file, indent=2)


def report_to_bencher(path: str = BMF_OUTPUT) -> None:
    """Write the BMF file at the end of the run. Call once, from the locustfile."""

    @events.quitting.add_listener
    def _on_quitting(environment, **kwargs):
        # Workers reset their stats after reporting them; only the master has the full picture.
        if isinstance(environment.runner, WorkerRunner):
            return

        write_bencher_metric_format(environment.stats, path)
