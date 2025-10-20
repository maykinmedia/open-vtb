======================================
Open Verzoek, Taken en Berichten (VTB)
======================================

:Version: 0.1.0
:Source: https://github.com/maykinmedia/open-vtb
:Keywords: ``verzoeken`` ``taken`` ``berichten``

|docs| |docker|

Register en API's voor Verzoeken, Taken en Berichten. (`English version`_)

Ontwikkeld door `Maykin B.V.`_ in opdracht van de 
`Platform Dienstverlening werkgroep`_.


Introductie
===========

Platform Dienstverlening verlegt de grens voor Zaakgericht Werken en 
introduceert een aantal concepten die aanvullende functionaliteit geven binnen
Platform Dienstverlening. Deze concepten zijn:

* **Verzoeken** Een ontkoppeling tussen een applicatie en een zaakregister, 
  waarin het verzoek de gegevens van de aanvraag (het verzoek) bevat. Op basis
  van dit verzoek kan een applicatie bepalen wat voor zaak dit moet worden.

* **Taken** Aanvullende vragen van de overheid aan de inwoner of ondernemer
  kunnen uitgezet worden als taken. Bijvoorbeeld voor het aanleveren van een
  document, of een uitstaande betaling. Een taak wordt typisch uitgezet door 
  een afhandelcomponent en wordt typisch weergegeven in een mijn-omgeving.

* **Berichten** Communicatie tussen inwoners, ondernemers en gemeenten via 
  digitale kanalen. Het vormt een naslag van alle communicatie die is verstuurd
  en ook is in te zien via bijvoorbeeld een mijn-omgeving of KCC-applicatie.


API specificatie
================

|oas|

==============  ==============  =============================
Versie          Release datum   API specificatie
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/main/src/openvtb/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/main/src/openvtb/api/openapi.yaml>`_,
                                (`verschillen <https://github.com/maykinmedia/open-vtb/compare/0.1.0..main#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
0.1.0           YYYY-MM-DD      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/api/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/open-vtb/0.1.0/src/openvtb/api/openapi.yaml>`_
==============  ==============  =============================

Vorige versies worden nog 6 maanden ondersteund nadat de volgende versie is 
uitgebracht.

Zie: `Alle versies en wijzigingen <https://github.com/maykinmedia/open-vtb/blob/main/CHANGELOG.rst>`_


Ontwikkelaars
=============

|build-status| |coverage| |ruff| |docker| |python-versions|

Deze repository bevat de broncode voor Open VTB. Om snel aan de slag
te gaan, raden we aan om de Docker image te gebruiken. Uiteraard kan je ook
het project zelf bouwen van de broncode. Zie hiervoor
`INSTALL.rst <INSTALL.rst>`_.

Quickstart
----------

1. Download en start Open VTB:

   .. code:: bash

      wget https://raw.githubusercontent.com/maykinmedia/open-vtb/main/docker-compose.yml
      docker-compose up -d --no-build
      docker-compose exec web src/manage.py loaddata demodata
      docker-compose exec web src/manage.py createsuperuser

2. In de browser, navigeer naar ``http://localhost:8000/`` om de beheerinterface
   en de API te benaderen.


Links
=====

* `Documentatie <https://open-vtb.readthedocs.io/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/open-vtb>`_
* `Issues <https://github.com/maykinmedia/open-vtb/issues>`_
* `Code <https://github.com/maykinmedia/open-vtb>`_
* `Community <https://TODO>`_


Licentie
========

Copyright © Maykin 2025

Licensed under the EUPL_


.. _`English version`: README.EN.rst

.. _`Maykin B.V.`: https://www.maykinmedia.nl

.. _`Platform Dienstverlening werkgroep`: https://dienstverleningsplatform.gitbook.io/

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
