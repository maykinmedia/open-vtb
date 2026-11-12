Performance test
================

Load tests for Open VTB, written with `Locust`_. Results are tracked over time
with `Bencher`_, which raises an alert when a change makes the API slower.

.. _Locust: https://locust.io/
.. _Bencher: https://bencher.dev/

What is tested
==============

A ``GET`` on the list endpoints of Verzoeken, Taken and Berichten, without filters,
with ``pageSize=100&page=10``.

Structure
=========

.. code-block:: text

    performance_test/
    ├── bencher_iqr_calculcator.py  # Suggests Bencher thresholds from the history of past runs
    ├── bencher.py                  # Writes the Locust results in the Bencher Metric Format (reusable)
    ├── tests.py                    # The Open VTB locustfile: which endpoints to hit
    └── locust/
        ├── __init__.py
        ├── locust.conf             # Load profile: users, duration, host
        └── utils.py                # Generic user and tasks for list endpoints (reusable)

Load profile
============

Defined in ``locust/locust.conf``:

* 20 users, started 10 per second;
* 2 minutes per run;
* statistics reset once all users are running, so the ramp-up is not measured.

Each user waits 1 to 3 seconds between requests, as set by ``wait_time`` on the
user class in ``locust/utils.py``.

Running locally
===============

Install the dependencies listed in ``requirements/performance-tests.in`` (they are pinned in ``requirements/ci.txt``).

1. Fill the database:

   .. code-block:: bash

       src/manage.py generate_data --count 50000

2. Start Open VTB with uWSGI:

   .. code-block:: bash

       SCRIPTPATH=bin DB_HOST=localhost UWSGI_PROCESSES=4 UWSGI_THREADS=1 bin/docker_start.sh

3. Run Locust:

   .. code-block:: bash

       locust --config performance_test/locust/locust.conf

Results file
============

At the end of the run, ``bencher.py`` writes the results in the `Bencher Metric Format`_ (BMF),
one benchmark per endpoint plus an ``aggregated`` benchmark over all requests.

Local file with results:  ``/tmp/bencher_metric_format.json``.

.. _Bencher Metric Format: https://bencher.dev/docs/reference/bencher-metric-format/

Measures
--------

All latencies are in nanoseconds, like Bencher's built-in ``latency`` measure.

============================  =========================================================
Measure                       Meaning
============================  =========================================================
``latency``                   95th percentile, with the median and the 99th percentile
                              as lower and upper value
``latency-p50``               Median: half of the requests are faster than this
``latency-mean``              Average response time
``latency-p75`` … ``p999``    Other percentiles
``latency-min``, ``-max``     Fastest and slowest request
``throughput``                Requests per second
``requests``                  Number of requests in the run
``response-size``             Average response size, in bytes
============================  =========================================================

``throughput`` mostly depends on the number of users Locust simulates, not on
the speed of the server: it is not a measure of capacity with this profile.

Continuous integration
======================

The ``Performance test`` GitHub Actions workflow (``.github/workflows/performance-testsest.yml``) runs the whole process on every push to ``main``, on every tag and on pull requests: it starts Open VTB with uWSGI,
generates the data, runs Locust and sends the results to Bencher.
On a pull request, Bencher compares the results with ``main`` and comments them on the PR.

Thresholds
==========

Bencher raises an alert when the median (``latency-p50``) or the average
(``latency-mean``) of a run is unusually high compared with the last 30 runs:
above the third quartile plus 2 times the interquartile range (IQR).
This adapts to how much the results normally vary, instead of using a fixed percentage.

A threshold only applies once there are at least 15 earlier runs: before that
there is too little history to tell a regression from normal variation.

Reading the results
===================

How to read the charts, and what the median, the 95th percentile and the
regression alerts mean, is explained in the `Performance`_ page of the
documentation, together with the live results from Bencher.

.. _Performance: https://open-vtb.readthedocs.io/en/latest/development/performance.html
