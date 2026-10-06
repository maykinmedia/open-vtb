==============
Change history
==============

0.2.0 (2026-10-06)
==================

.. note::

  The environment variable used to configure the uWSGI port in the Docker
  entrypoint has been renamed from ``UWSGI_PORT`` to ``OPENVTB_PORT``
  (see :ref:`installation_env_config`). Deployments that override the uWSGI
  port need to update their configuration accordingly.

**New features**

* [:open-vtb:`101`] Add the ``medeInitiator`` attribute to ``Verzoek``
* [:open-vtb:`112`] Limit the possible values of the ``handelingsperspectief`` attribute to the defined enum
* [:open-vtb:`124`] Add API filters for:

    * ``/verzoeken``
    * ``/taken``
    * ``/berichten``

* [:open-vtb:`125`] Add the ``ontvangenBijlagen`` attribute to ``URLTaken``
* [:open-vtb:`179`] Improve the ``urn`` filters logic to correctly handle URN values. See the API specification descriptions for examples

**Bugfixes**

* [:open-vtb:`110`] Update help_text for ``Bericht.referentie``

**Project maintenance**

* [:open-api-framework:`218`] Add Zizmor GitHub Actions security scanning and updated workflows
* [:open-api-workflows:`64`] Add action to generate and update Docker Hub description
* [:open-api-workflows:`60`] Upgrade ``open-api-workflows`` to ``v7.0.0`` and reenable OAS workflow and replace spectral-cli with vacuum
* [:open-api-framework:`228`] Add environment variable ``CELERY_RESULT_EXPIRES`` to change how long the results will be stored in Redis (see :ref:`installation_env_config` > Celery for more information)

* Upgrade python deps to fix security warnings

  * ``django`` to 5.2.17
  * ``django-log-outgoing-requests`` to 0.9.1
  * ``django-privates`` to 4.0.3
  * ``django-simple-certmanager`` to 4.0.0
  * ``djangorestframework`` to 3.18.1
  * ``djangorestframework-gis`` to 1.3.0
  * ``open-api-framework`` to 0.16.0
  * ``commonground-api-common`` to 3.0.0
  * ``bleach`` to 6.4.0
  * ``cryptography`` to 50.0.0
  * ``maykin-common`` to 0.22.0
  * ``notifications-api-common`` to 0.13.1
  * ``pyjwt`` to 2.15.1
  * ``pyopenssl`` to 26.4.0
  * ``urllib3`` to 2.8.0
  * ``tornado`` to 6.5.10
  * ``vcrpy`` to 8.3.0
  * ``zgw-consumers`` to 2.1.0
  * ``sqlparse`` to 0.6.0

**Documentation**

* [:open-api-framework:`217`] Update application and repository branding by applying the new icons and logos

0.1.0 (27-05-2026)
==================

Initial release of Open VTB.

Features:

* Verzoeken API
* Taken API
* Berichten API
