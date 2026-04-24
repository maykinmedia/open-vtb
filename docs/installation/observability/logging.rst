.. _installation_observability_logging:

=======
Logging
=======

Logging is the practice of emitting log messages that describe what is happening in the
system, or "events" in short. Log events can have varying degrees of severity, such as
``debug``, ``info``, ``warning``, ``error`` or even ``critical``. By default, Open VTB
emits logs with level ``info`` and higher.

A collection of log events with a correlation ID (like a request or trace ID) allow one
to reconstruct the chain of events that took place which lead to a particular outcome.

Open VTB emits structured logs in JSON format (unless explicitly configured otherwise),
which should make log aggregation and analysis easier.

We try to keep a consistent log message structure, where the following keys
are (usually) present:

``source``
    The component in the application stack that produced the log entry. Typical
    values are ``uwsgi`` and ``app``.

``level``
    The severity level of the log message. One of ``debug``, ``info``, ``warning``,
    ``error`` or ``critical``.

``timestamp``
    The moment when the log entry was produced, a string in ISO-8601 format. Most of
    the logs have microsecond precision, but some of them are limited to second
    precision.

``event``
    The event that occurred, e.g. ``request_started`` or ``spawned worker (PID 123)``.
    This gives the semantic meaning to the log entry.

Other keys that frequently occur are:

``request_id``
    Present for application logs emitted during an HTTP request, makes it possible to
    correlate multiple log entries for a single request. Not available in logs emitted
    by background tasks or logs emitted before/after the Open VTB app.

.. tip:: Certain log aggregation solutions require you to configure "labels" to extract
   for efficient querying. You can use the above summary of log context keys to configure
   this according to your needs.

.. note:: We can not 100% guarantee that every log message will always be JSON due to
   limitations in third party software/packages that we use. Most (if not all) log
   aggregation technologies support handling both structured and unstructured logs.


.. _manual_logging:

Logging
=======

Format
------

Open VTB emits structured logs (using `structlog <https://www.structlog.org/en/stable/>`_).
A log line can be formatted like this:

.. code-block:: json

    {
        "uuid": "20d23f12-6743-486c-a1f2-c31c5c6a86f9",
        "identificatie": "ABC-1",
        "source": "app",
        "event": "verzoek_created",
        "user_id": null,
        "request_id": "2f9e9a5b-d549-4faa-a411-594aa8a52eee",
        "timestamp": "2026-01-01T14:09:20.339166Z",
        "logger": "openvtb.components.verzoeken.api.viewsets",
        "level": "info"
    }

Each log line will contain an ``event`` type, a ``timestamp`` and a ``level``.
Dependent on your configured ``LOG_LEVEL`` (see :ref:`installation_env_config` for more information),
only log lines with of that level or higher will be emitted.

.. _manual_logging_exceptions:

Exceptions
----------

Handled exceptions follow a standardized JSON format to ensure consistency and improve error tracking.
Most fields are standard and include:
``title``, ``code``, ``status``, ``event``, ``source``, ``user_id``, ``request_id``, ``exception_id``, ``timestamp``, ``logger`` and ``level``.

A new field ``invalid_params`` has been added to provide detailed information about which input parameters caused the error in API calls.

    - ``name``: name of the invalid parameter
    - ``code``: specific error code
    - ``reason``: explanation/message of the error

.. code-block:: json

    {
        "title": "'Je hebt geen toestemming om deze actie uit te voeren.'",
        "code": "invalid-client-identifier",
        "status": 403,
        "invalid_params": [
            {
                "name": "",
                "code": "invalid-client-identifier",
                "reason": "Client identifier bestaat niet"
            }
        ],
        "event": "api.handled_exception",
        "exception_id": "96af71a2-5b1d-40db-b177-f595cbf0f847",
        "source": "app",
        "timestamp": "2026-01-01T09:55:43.796277Z",
        "logger": "vng_api_common.exception_handling",
        "level": "error"
    }

Uncaught exceptions that occur via the API are logged as ``api.uncaught_exception`` events
and contain the traceback of the exception.

.. code-block:: json

    {
        "message": "division by zero",
        "event": "api.uncaught_exception",
        "source": "app",
        "timestamp": "2026-01-01T14:40:06.276604Z",
        "logger": "vng_api_common.views",
        "level": "error",
        "exception": "Traceback (most recent call last):\n  File \"/usr/local/lib/python3.12/site-packages/rest_framework/views.py\", line 497, in dispatch\n    self.initial(request, *args, **kwargs)\n  File \"/usr/local/lib/python3.12/site-packages/vng_api_common/geo.py\", line 30, in initial\n    super().initial(request, *args, **kwargs)\n  File \"/usr/local/lib/python3.12/site-packages/rest_framework/views.py\", line 415, in initial\n    self.check_permissions(request)\n  File \"/usr/local/lib/python3.12/site-packages/rest_framework/views.py\", line 332, in check_permissions\n    if not permission.has_permission(request, self):\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/openvtb/utils/decorators.py\", line 53, in convert_exceptions\n    response = function(*args, **kwargs)\n               ^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/openvtb/utils/permissions.py\", line 122, in has_permission\n    1 / 0\n    ~^~~\nZeroDivisionError: division by zero"
    }

Third party library events
--------------------------

For more information about log events emitted by third party libraries, refer to the documentation
for that particular library

* :ref:`Django (via django-structlog) <request_events>`
* :ref:`Celery (via django-structlog) <request_events>`
