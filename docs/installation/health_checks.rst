.. _installation_health_checks:

=======================
Container health checks
=======================

Open VTB is deployed as a collection of containers.
Containers can be checked if they're running as expected, and actions can be taken by
the container runtime or container orchestration (like Kubernetes and Docker) when that's not the case,
like restarting the container or removing it from the pool that serves traffic.

Health checks are responsible for detecting anomalies and reporting that a container is
not running as expected. They can take different forms, for example:

* running a script and checking the exit code of the process
* making an HTTP request to an endpoint which responds with a success or error status
  code
* opening a TCP connection to a particular port

This section of the documentation describes the recommended health checks to use that
are provided in Open VTB, or the health checks to implement in containers of third
party software typically used in an Open VTB deployment. You can incorporate these in
your infrastructure code (like Helm charts).

You can find code examples of these health checks in our `docker-compose.yml`_ on Github.

.. _docker-compose.yml: https://github.com/maykinmedia/open-vtb/blob/main/docker-compose.yml

.. contents:: Jump to
    :local:
    :depth: 2
    :backlinks: none

Open VTB containers
===================

HTTP service
------------

The Open VTB web service listens on port 8000 inside the container and accepts HTTP
traffic. Three endpoints are exposed for health checks.

``http://localhost:8000/_healthz/livez/``
    The liveness endpoint - checks that HTTP requests can be handled. Suitable for
    liveness (and readiness) probes. This is the check with lowest overhead.

``http://localhost:8000/_healthz/``
    Endpoint that checks connections with database, caches, database migration state...

    Suitable for the startup probe. The most expensive check to run, as it checks all
    dependencies of the application.

``http://localhost:8000/_healthz/readyz/``
    The readiness endpoint - checks that requests can be handled and tests that the
    default cache (used by for sessions) and database connection function. Slightly
    more expensive than the liveness check, but it's a good candidate for the readiness
    probe.

.. tip:: Ensure the ``ALLOWED_HOSTS`` environment variable contains ``localhost``. See
    :ref:`installation_env_config` for more details.

.. tip:: The executable ``maykin-common`` is available in the container which can be
   used to perform the health checks, as an alternative to HTTP probes.

   .. code-block:: bash

        maykin-common health-check \
            --endpoint=http://localhost:8000/_healthz/livez/ \
            --timeout=3


Third party containers
======================

Redis
-----

The Redis container images include a command line utility - ``redis-cli`` which
has a ``ping`` command to test connectivity to the server:

.. code-block:: bash

    redis-cli ping

The command exits with exit code ``0`` on success and exit code ``1`` on failure.

PostgreSQL
----------

.. warning:: Running the database as a container can bring certain scaling and disaster
   recovery challenges. We only provide this check for completeness sake.

PostgreSQL container images typically include the ``pg_isready`` binary, which tests
the database connection (accepting traffic on the specified host and port). It has a
non-zero exit code when the database is not ready.
