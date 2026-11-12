.. _performance:

=================
Performance Tests
=================

Open VTB is load tested on every change to ``main`` and on every release. The
results are tracked over time with `Bencher`_, which raises an alert when a
change makes the API slower. The charts on this page are loaded live from
Bencher

.. _Bencher: https://bencher.dev/perf/open-vtb

What is measured
================

The load test sends ``GET`` requests to the list endpoints of the three
components, without filters, asking for page 10 with 100 items per page:

* Verzoeken: ``/verzoeken/api/v1/verzoeken``
* Taken: ``/taken/api/v1/externetaken``
* Berichten: ``/berichten/api/v1/berichten``

Test setup
==========

=====================  ==========================================================
Server                 uWSGI, 4 processes, 1 thread
Database               PostgreSQL, 50,000 generated items
Load                   20 simultaneous users, each waiting 1 to 3 seconds
                       between requests
Duration               2 minutes per run, ramp-up excluded from the results
Environment            GitHub Actions runner
=====================  ==========================================================

.. note::

   These numbers describe Open VTB in this specific setup. Response times in a
   real installation depend on its hardware, its configuration and its data, and
   will be different. They are meant to compare versions of Open VTB with each
   other, not to size an installation.

Results
=======

Median response time
--------------------

Half of the requests are answered faster than this. It is the most stable
measure, and the one used to detect regressions.

.. raw:: html

    <iframe src="https://bencher.dev/perf/open-vtb/embed?branches=01a1bfbe-9720-717b-b958-65b118a4121d,01a1c0be-17fd-74a0-bf23-7f671da8f1ee&amp;testbeds=01a1c0be-17ff-77bc-8fd3-7ef281c405d1&amp;benchmarks=01a1bfbe-972c-7152-b7e4-de98aa867d91,01a1bfbe-9725-71be-8424-1ffdae388190,01a1bfbe-972b-73f5-b148-5491533c37f4&amp;measures=01a1bfbe-9729-7414-ba5c-f6cebf90bcc4&amp;window=92d&amp;y_axis=linear" title="Median response time | open-vtb" width="100%" height="700" style="border: 0" loading="lazy"></iframe>

Response time of 95% of the requests
------------------------------------

95 out of 100 requests are answered faster than this. It shows how slow the
slower requests get, and varies more from one run to the next.

.. raw:: html

    <iframe src="https://bencher.dev/perf/open-vtb/embed?branches=01a1c0be-17fd-74a0-bf23-7f671da8f1ee,01a1bfbe-9720-717b-b958-65b118a4121d&amp;testbeds=01a1c0be-17ff-77bc-8fd3-7ef281c405d1&amp;benchmarks=01a1bfbe-972c-7152-b7e4-de98aa867d91,01a1bfbe-9725-71be-8424-1ffdae388190,01a1bfbe-972b-73f5-b148-5491533c37f4&amp;measures=01a1bfbe-9728-72fd-b41a-3b75e6560634&amp;window=92d&amp;y_axis=linear" title="Response time of 95% of the requests | open-vtb" width="100%" height="700" style="border: 0" loading="lazy"></iframe>

Releases
--------

One point per release, to compare versions of Open VTB with each other.

.. raw:: html

    <iframe src="https://bencher.dev/perf/open-vtb/embed?branches=01a1bfbe-9720-717b-b958-65b118a4121d,01a1c0be-17fd-74a0-bf23-7f671da8f1ee&amp;testbeds=01a1c0be-17ff-77bc-8fd3-7ef281c405d1&amp;benchmarks=01a1bfbe-972c-7152-b7e4-de98aa867d91,01a1bfbe-9725-71be-8424-1ffdae388190,01a1bfbe-972b-73f5-b148-5491533c37f4&amp;measures=01a1bfbe-9729-7414-ba5c-f6cebf90bcc4&amp;window=92d&amp;x_axis=version&amp;y_axis=linear" title="Median response time per release | open-vtb" width="100%" height="700" style="border: 0" loading="lazy"></iframe>

Reading the results
===================

Median
    The typical response time. A sudden step up after a change is a regression.

95th percentile
    How long the slower requests take. A large gap with the median means a small
    share of the requests is regularly much slower than the rest.

Regressions
    Every run is compared with the last 30 runs. When the median or the average
    is unusually high, above the third quartile plus 2 times the interquartile
    range (IQR), Bencher raises an alert. The threshold adapts to how much the
    results normally vary, and only applies once there are at least 15 earlier
    runs. On a pull request, the alert shows up in the comment Bencher posts with
    the results.

Running the load test
=====================

The load test lives in the ``performance_test`` folder of the repository, whose
`README`_ explains how to run it locally and how it is set up in continuous
integration.

.. _README: https://github.com/maykinmedia/open-vtb/blob/main/performance_test/README.rst
