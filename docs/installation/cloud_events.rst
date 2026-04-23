.. _cloud_events:

============
Cloud events
============

-------------
Configuration
-------------

These cloud events can be sent to Open Notificaties, which can route the events to subscribed
webhooks. To ensure reliable delivery of events, proper configuration is required in both **Open VTB** and **Open Notificaties**.
This includes enabling CloudEvents support, configuring source metadata, and setting up the connection between both systems.

CloudEvents follow a standardized event format (**CloudEvents 1.0**), enabling consistent communication between systems
and supporting loose coupling between producers and consumers.

Open VTB
--------

1. Make sure the following environment variables are configured (see :ref:`installation_env_config`)

   * ``ENABLE_CLOUD_EVENTS``: set this to ``True``.
   * ``NOTIFICATIONS_SOURCE``: set this to the value that should be used in the ``source``
     field for cloud events (e.g. ``urn:nld:oin:01823288444:berichtensysteem``).
   * ``SITE_DOMAIN``: set this to the primary domain Open VTB is hosted on (e.g. ``open-vtb.gemeente.nl``).

2. Make sure the connection with Open Notificaties is configured via ``setup_configuration``.
   See :ref:`installation_configuration_cli` for more information.

Alternatively, if ``setup_configuration`` is not used for programmatic configuration,
the connection with Open Notificaties can be configured manually via the admin interface.
For more information on how to do this, see :ref:`installation_configuration`.

Open Notificaties
-----------------

For the required configuration in Open Notificaties, see the Open Notificaties documentation.

------
Events
------

Open VTB emits the following **CloudEvents**:

* ``nl.overheid.berichten.bericht-geregistreerd``: this event is emitted whenever a new message is created in the system.

  * Trigger: `POST /berichten`
  * Indicates that the message has been successfully registered, but it is not yet available for consumption.


* ``nl.overheid.berichten.bericht-gepubliceerd``: this event is emitted asynchronously when the message reaches its configured `publicatiedatum`.

  * Trigger: periodic task executed via **Celery Beat**
  * Indicates that the message is now active and may be displayed, processed, forwarded, or used for notifications by consuming systems.


Example of a ``nl.overheid.berichten.bericht-gepubliceerd`` cloud event in its current shape:

.. code-block:: json

        {
            "id": "f347fd1f-dac1-4870-9dd0-f6c00edf4bf7",
            "source": "urn:nld:oin:01823288444:berichtensysteem",
            "specversion": "1.0",
            "type": "nl.overheid.berichten.bericht-gepubliceerd",
            "subject": "ca66b713-ffab-4424-a9a2-2d2c233424c8",
            "time": "2026-01-01T00:00:00Z",
            "dataref": null,
            "datacontenttype": "application/json",
            "data": {
                "onderwerp": "ontvanger",
                "publicatiedatum": "2026-01-01T00:00:00Z",
                "ontvanger": "urn:ontvanger:123456"
            }
        }
