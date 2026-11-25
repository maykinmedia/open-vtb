.. _installation_prerequisites:

Prerequisites
=============

Open VTB is most often deployed as a Docker container. While the
`container images <https://hub.docker.com/r/maykinmedia/open-vtb>`_ contain all the
necessary dependencies, Open VTB does require extra service to deploy the full stack.
These dependencies and their supported versions are documented here.

The ``docker-compose.yml`` (not suitable for production usage!) in the root of the
repository also describes these dependencies.

PostgreSQL with Postgis
-----------------------

.. warning::

   Since Open VTB version 0.2.0, PostgreSQL version 14 or higher is required. Attempting
   to deploy this version of Open VTB with PostgreSQL 13 or lower will result in errors!

Open VTB currently only supports PostgreSQL as datastore.

The supported versions in the table below are tested in the CI pipeline. Other versions
*may* work but we offer no guarantees.

============ ============ ============ ============ ============
Matrix       Postgres 15  Postgres 16  Postgres 17  Postgres 18
============ ============ ============ ============ ============
Postgis 3.6  V            V            V            V
Postgis 3.7  V            V            V            V
============ ============ ============ ============ ============

.. warning:: Open VTB only supports maintained versions of PostgreSQL. Once a version is
   `EOL <https://www.postgresql.org/support/versioning/>`_, support will
   be dropped in the next release.

.. _postgis: https://postgis.net/