#!/usr/bin/env python
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "msgspec~=0.19.0",
#   "numpy~=2.2",
#   "requests~=2.32.4",
#   "scipy~=1.15",
#   "typer~=0.27.0",
# ]
# ///
#
# Usage:
#
# .. code-block:: bash
#
#     uv run ./bencher_iqr_calculcator.py --list
#     uv run ./bencher_iqr_calculcator.py --benchmark-name="<name>"
#     uv run ./bencher_iqr_calculcator.py --all [--json] [<report-file>]
#
"""
Bencher IQR Calculator

Calculates Interquartile Range (IQR) statistics from Bencher report JSON
to help determine appropriate threshold boundaries for noisy CI environments.
"""

from __future__ import annotations

from collections.abc import Iterable
from itertools import chain
from pathlib import Path
from typing import Annotated

import msgspec
import numpy as np
import requests
import typer
from msgspec.json import decode, encode
from scipy.stats import iqr

REPORTS_URL = (
    "https://api.bencher.dev/v0/projects/objects-ed2ce35-z71n5gf8t4f40/reports"
    "?per_page=100"
)

app = typer.Typer(
    help="Analyze Bencher reports for IQR thresholds",
    add_completion=False,
    no_args_is_help=False,
)


class Metric(msgspec.Struct, frozen=True):
    value: float


class Alert(msgspec.Struct, frozen=True):
    benchmark: Benchmark
    metric: Metric


class Benchmark(msgspec.Struct, frozen=True, order=True):
    slug: str
    name: str

    def __str__(self) -> str:
        return self.name


class MeasureDef(msgspec.Struct, frozen=True):
    name: str


class MeasureEntry(msgspec.Struct, frozen=True):
    measure: MeasureDef
    metric: Metric


class ResultItem(msgspec.Struct, frozen=True):
    benchmark: Benchmark
    measures: list[MeasureEntry]


class Report(msgspec.Struct, frozen=True):
    results: list[list[ResultItem]]
    alerts: list[Alert] = []


def extract_metric_values(
    report: Report,
    benchmark_filter: str = "",
    measure_filter: str = "",
) -> Iterable[float]:
    """Extract metric values from Bencher report JSON structure."""
    for result in report.results:
        for item in result:
            if benchmark_filter and benchmark_filter != str(item.benchmark):
                continue
            for measure in item.measures:
                if measure_filter:
                    meas_def = measure.measure
                    if measure_filter.lower() != meas_def.name.lower():
                        continue

                yield measure.metric.value


def benchmarks(reports: Iterable[Report]) -> set[Benchmark]:
    return {
        item.benchmark
        for report in reports
        for outer_list in report.results
        for item in outer_list
    }


def calculate_iqr_statistics(values: Iterable[float]) -> dict[str, float]:
    """Calculate IQR-based statistics with skew guards."""
    arr = np.fromiter(values, dtype=float)
    arr = arr[np.isfinite(arr)]

    if len(arr) < 2:
        raise ValueError(
            "At least 2 valid numeric data points are required to calculate statistics"
        )

    iqr_val = iqr(arr)
    q1, q3 = np.percentile(arr, [25, 75])
    median_val = float(np.median(arr))
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr, ddof=1))

    # Compute Median Absolute Deviation (MAD) as an extra robustness layer
    mad_val = float(np.median(np.abs(arr - median_val)))

    return {
        "count": int(len(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": mean_val,
        "median": median_val,
        "std": std_val,
        "q1": q1,
        "q3": q3,
        "iqr": iqr_val,
        "mad": mad_val,
        # Outlier fences: Clamped to 0.0 because physical values like latency cannot be negative
        "lower_fence_1.5x": max(0.0, q1 - 1.5 * iqr_val),
        "upper_fence_1.5x": q3 + 1.5 * iqr_val,
        "lower_fence_3x": max(0.0, q1 - 3.0 * iqr_val),
        "upper_fence_3x": q3 + 3.0 * iqr_val,
        # High tail percentiles
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        # Relative Dispersion Metrics
        "coefficient_of_variation_pct": float((std_val / mean_val) * 100)
        if mean_val != 0
        else 0.0,
        "non_parametric_cv_pct": float((iqr_val / median_val) * 100)
        if median_val != 0
        else 0.0,
        "max_deviation_from_median_pct": float(
            ((np.max(arr) - median_val) / median_val) * 100
        )
        if median_val != 0
        else 0.0,
        "range_vs_median_pct": float(((np.max(arr) - np.min(arr)) / median_val) * 100)
        if median_val != 0
        else 0.0,
    }


def format_report(stats: dict[str, float]) -> str:
    """Pretty-print analysis summary with actionable Bencher threshold guidance."""

    # 1. Determine baseline noise using Robust (Non-Parametric) CV
    # This prevents a single massive GHA spike from skewing our perception of the typical variance.
    rcv = stats["non_parametric_cv_pct"]
    if rcv < 5.0:
        noise_level = "LOW (Stable environment)"
        rec_test = "iqr (or percentage)"
        rec_mult = "1.5"
    elif rcv <= 15.0:
        noise_level = "MODERATE (Typical cloud instance)"
        rec_test = "iqr"
        rec_mult = "2.0"
    else:
        noise_level = "HIGH / EXTREME (Public GHA Runner baseline)"
        rec_test = "iqr"
        rec_mult = "2.5 or 3.0"

    # 2. Check for severe right-tail skew (Classic GHA noisy neighbor behavior)
    # If the P95/P99 tail eclipses the 1.5x IQR fence, 1.5x will trigger constant false alarms.
    false_alarm_risk = "LOW"
    if stats["p95"] > stats["upper_fence_1.5x"]:
        false_alarm_risk = "HIGH (Tail spikes regularly bypass the standard 1.5x fence)"
        if rec_mult == "2.0":
            rec_mult = "2.5"

    # 3. Dynamic simple percentage calculation based on P95 instead of Max
    # (Protects your threshold from latching onto a single ancient 500% spike)
    rec_percentage = ((stats["p95"] - stats["median"]) / stats["median"]) + 0.15

    lines = [
        "=" * 65,
        "                     BENCHER IQR ANALYSIS REPORT",
        "=" * 65,
        f"Samples Evaluated:               {stats['count']}",
        "",
        "--- CENTRAL TENDENCY & CLASSIC DISPERSION ---",
        f"Min / Median / Max:              {stats['min']:.4f} / {stats['median']:.4f} / {stats['max']:.4f}",
        f"Mean:                            {stats['mean']:.4f}",
        f"Std Dev (Classical):             {stats['std']:.4f} ({stats['coefficient_of_variation_pct']:.1f}% CV)",
        "",
        "--- ROBUST DISPERSION (Resilient to Spikes) ---",
        f"Q1 / Q3:                         {stats['q1']:.4f} / {stats['q3']:.4f}",
        f"IQR (Q3-Q1):                     {stats['iqr']:.4f}",
        f"Median Absolute Deviation (MAD): {stats['mad']:.4f}",
        f"Robust CV (IQR/Median):          {rcv:.1f}%",
        "",
        "--- OUTLIER FENCES (Tukey Method, Clamped) ---",
        f"Mild Upper Fence (1.5×IQR):      {stats['upper_fence_1.5x']:.4f}",
        f"Severe Upper Fence (3.0×IQR):    {stats['upper_fence_3x']:.4f}",
        f"Lower Fences (1.5x / 3.0x):      {stats['lower_fence_1.5x']:.4f} / {stats['lower_fence_3x']:.4f}",
        "",
        "--- TAIL PERCENTILES ---",
        f"P90 / P95 / P99:                 {stats['p90']:.4f} / {stats['p95']:.4f} / {stats['p99']:.4f}",
        f"Max Deviation from Median:       {stats['max_deviation_from_median_pct']:.1f}%",
        "",
        "=" * 65,
        "                 ENVIRONMENT & THRESHOLD ANALYSIS",
        "=" * 65,
        f"Detected Noise Profile:          {noise_level}",
        f"False Alarm Risk at 1.5x IQR:    {false_alarm_risk}",
        f"Historical Max Range Spread:     {stats['range_vs_median_pct']:.1f}% of median",
        "",
        "--- RECOMMENDED CLI CONFIGURATIONS FOR PUBLIC GHA ---",
    ]

    if rec_test == "iqr":
        lines.extend(
            [
                "👉 OPTION A: Robust IQR Test (Highly Recommended for GHA)",
                "   Filters out hypervisor noise and isolates your actual code performance.",
                "   Execute Bencher with these parameters:",
                "     --threshold-test iqr \\",
                f"     --threshold-upper-boundary {rec_mult} \\",
                "     --threshold-window 30 \\",
                "     --threshold-min-sample-size 15",
                "",
            ]
        )

    lines.extend(
        [
            "👉 OPTION B: Tail-Guarded Percentage Test (Fallback)",
            "   Useful if your internal framework has already pre-aggregated iterations to a minimum.",
            "     --threshold-test percentage \\",
            f"     --threshold-upper-boundary {max(0.10, rec_percentage):.2f}  # Allows a ~{int(max(0.10, rec_percentage) * 100)}% regression baseline",
            "",
            "💡 DESIGN ADVICE FOR PUBLIC RUNNERS:",
            f"   * Window Size: Your current max range spread is {stats['range_vs_median_pct']:.1f}%.",
            "     Keep '--threshold-window 30' or higher. A wide rolling window forces Bencher to",
            "     evaluate current builds against a broad history, neutralizing localized GHA noise waves.",
            "   * If false alerts persist, switch your benchmarking framework to report the 'median' or",
            "     'minimum' execution duration per test, rather than the arithmetic 'mean'.",
            "=" * 65,
        ]
    )

    return "\n".join(lines)


def load_reports(report_file: Path | None) -> list[Report]:
    """Load reports from a local JSON file, or fetch them from the Bencher API."""
    try:
        if report_file:
            data = report_file.read_bytes()
        else:
            response = requests.get(REPORTS_URL, timeout=30)
            response.raise_for_status()
            data = response.content
        return decode(data, type=list[Report])
    except (OSError, requests.RequestException, msgspec.DecodeError) as e:
        typer.secho(f"Error loading reports: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e


def list_benchmarks(reports: Iterable[Report], *, err: bool = False) -> None:
    for b in sorted(benchmarks(reports)):
        typer.echo(f'--benchmark-name="{b}"', err=err)


@app.command()
def main(
    report_file: Annotated[
        Path | None,
        typer.Argument(
            help="JSON file with Bencher report data (default: fetch from the Bencher API)",
            exists=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    benchmark_name: Annotated[
        str | None,
        typer.Option("--benchmark-name", "-b", help="Filter by benchmark name"),
    ] = None,
    measure: Annotated[
        str,
        typer.Option("--measure", "-m", help="Filter by measure name (e.g. 'latency')"),
    ] = "latency",
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON stats")
    ] = False,
    list_only: Annotated[
        bool, typer.Option("--list", help="List benchmarks and exit")
    ] = False,
    analyse_all: Annotated[
        bool, typer.Option("--all", help="Analyse all benchmarks")
    ] = False,
) -> None:
    """Analyze Bencher reports and suggest IQR threshold settings."""
    reports = load_reports(report_file)

    if list_only:
        list_benchmarks(reports)
        raise typer.Exit()

    if benchmark_name:
        benches: list[str] = [benchmark_name]
    elif analyse_all:
        benches = [str(b) for b in sorted(benchmarks(reports))]
    else:
        typer.secho(
            "No --benchmark-name nor --all provided. Available benchmarks:",
            fg=typer.colors.YELLOW,
            err=True,
        )
        list_benchmarks(reports, err=True)
        raise typer.Exit(code=1)

    for benchmark in benches:
        values = chain.from_iterable(
            extract_metric_values(report, benchmark, measure) for report in reports
        )

        try:
            stats_dict = calculate_iqr_statistics(values)
        except ValueError as e:
            typer.secho(f"{benchmark}: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from e

        if json_output:
            typer.echo(encode(stats_dict).decode())
        else:
            typer.echo()
            typer.echo(benchmark)
            typer.echo(format_report(stats_dict))


if __name__ == "__main__":
    app()
