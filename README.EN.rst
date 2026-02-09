======================================
Open Verzoek, Taken en Berichten (VTB)
======================================

:Version: 0.1.0
:Source: https://github.com/maykinmedia/open-vtb
:Keywords: ``verzoeken`` ``taken`` ``berichten``

|docs| |docker|

Register and API's for Verzoeken (Requests), Taken (Tasks) en Berichten
(Messages). (`Nederlandse versie`_)

Developed by `Maykin B.V.`_ for `Platform Dienstverlening working group`_.


Introduction
============

Platform Dienstverlening pushes the boundaries of case-oriented working and
introduces several concepts that provide additional functionality within
Platform Dienstverlening. These concepts are:

* **Verzoeken (Requests)** A decoupling between an application and a case
  register, in which the request contains the details of the request. Based on
  this request, an application can determine what type of case it should be.

* **Taken (Tasks)** Additional questions from the government to the resident or
  business owner can be assigned as tasks. For example, for submitting a
  document or an outstanding payment. A task is typically assigned by a
  client-application and is typically displayed in a portal.

* **Berichten (Messages)** Communication between residents, businesses, and
  municipalities via digital channels. It provides a record of all
  communication that has been sent and can also be viewed via, for example, a
  portal or servicedesk application.


API specification
=================

|oas|


================  =========================  =============   =================
Open VTB Version  API Version                Release date    API specification
================  =========================  =============   =================
main/latest        n/a                        n/a             | Verzoeken:
                                                                 `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/master/src/openvtb/components/verzoeken/openapi.yaml>`_,
                                                                 `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/master/src/openvtb/components/verzoeken/openapi.yaml>`_,
                                                                 (`diff <https://github.com/maykinmedia/open-vtb/compare/0.1.0..master>`_)
                                                              | Taken:
                                                                 `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/master/src/openvtb/components/taken/openapi.yaml>`_,
                                                                 `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/master/src/openvtb/components/taken/openapi.yaml>`_,
                                                                 (`diff <https://github.com/maykinmedia/open-vtb/compare/0.1.0..master>`_)
                                                              | Berichten:
                                                                 `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/master/src/openvtb/components/berichten/openapi.yaml>`_,
                                                                 `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/master/src/openvtb/components/berichten/openapi.yaml>`_,
                                                                 (`diff <https://github.com/maykinmedia/open-vtb/compare/0.1.0..master>`_)

0.1.0              | Verzoeken: 0.1.0        YYYY-MM-DD        | Verzoeken:
                   | Taken: 0.1.0                               `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/components/verzoeken/openapi.yaml>`_,
                   | Berichten: 0.1.0                           `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/components/verzoeken/openapi.yaml>`_,
                                                                 (`diff <https://github.com/maykinmedia/open-vtb/compare/0.0.0..0.1.0>`_)
                                                               | Taken:
                                                                 `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/components/taken/openapi.yaml>`_,
                                                                 `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/components/taken/openapi.yaml>`_,
                                                                 (`diff <https://github.com/maykinmedia/open-vtb/compare/0.0.0..0.1.0>`_)
                                                               | Berichten:
                                                                 `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/components/berichten/openapi.yaml>`_,
                                                                 `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/components/berichten/openapi.yaml>`_,
                                                                 (`diff <https://github.com/maykinmedia/open-vtb/compare/0.0.0..0.1.0>`_)
================  =========================  =============   =================




Previous versions are supported for 6 month after the next version is released.

See: `All versions and changes <https://github.com/maykinmedia/open-vtb/blob/main/CHANGELOG.rst>`_


Developers
==========

|build-status| |coverage| |ruff| |docker| |python-versions|

This repository contains the source code for openvtb. To quickly
get started, we recommend using the Docker image. You can also build the
project from the source code. For this, please look at
`INSTALL.rst <INSTALL.rst>`_.

Quickstart
----------

1. Download and run Open VTB:

   .. code:: bash

      wget https://raw.githubusercontent.com/maykinmedia/open-vtb/main/docker-compose.yml
      docker-compose up -d --no-build
      docker-compose exec web src/manage.py loaddata demodata
      docker-compose exec web src/manage.py createsuperuser

2. In the browser, navigate to ``http://localhost:8000/`` to access the admin
   and the API.


References
==========

* `Documentation <https://open-vtb.readthedocs.io/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/open-vtb>`_
* `Issues <https://github.com/maykinmedia/open-vtb/issues>`_
* `Code <https://github.com/maykinmedia/open-vtb>`_
* `Community <https://TODO>`_


License
=======

Copyright © Maykin 2025

Licensed under the EUPL_


.. _`Nederlandse versie`: README.rst

.. _`Maykin B.V.`: https://www.maykinmedia.nl

.. _`Platform Dienstverlening working group`: https://dienstverleningsplatform.gitbook.io/

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/open-vtb/actions/workflows/ci.yml/badge.svg?branch=main
    :alt: Build status
    :target: https://github.com/maykinmedia/open-vtb/actions/workflows/ci.yml

.. |docs| image:: https://readthedocs.org/projects/open-vtb/badge/?version=latest
    :target: https://open-vtb.readthedocs.io/
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/maykinmedia/open-vtb/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/open-vtb

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |docker| image:: https://img.shields.io/docker/v/maykinmedia/open-vtb?sort=semver
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/open-vtb

.. |python-versions| image:: https://img.shields.io/badge/python-3.12%2B-blue.svg
    :alt: Supported Python version

.. |oas| image:: https://github.com/maykinmedia/open-vtb/actions/workflows/oas.yml/badge.svg
    :alt: OpenAPI specification checks
    :target: https://github.com/maykinmedia/open-vtb/actions/workflows/oas.yml
