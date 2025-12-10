.. _manual_oidc:

==========================
Configuring OpenID Connect
==========================

Open VTB ondersteunt Single Sign On (SSO) via het OpenID Connect protocol (OIDC) voor de beheerinterface.

Gebruikers kunnen op die manier inloggen op Open VTB met hun account bij de OpenID Connect provider. In deze flow:

1. Klikt een gebruiker op het inlogscherm op *Inloggen met OIDC*
2. De gebruiker wordt naar de omgeving van de OpenID Connect provider geleid (bijv. Keycloak) waar ze inloggen met gebruikersnaam
   en wachtwoord (en eventuele Multi Factor Authentication)
3. De OIDC omgeving stuurt de gebruiker terug naar Open VTB (waar de account aangemaakt
   wordt indien die nog niet bestaat)
4. Een beheerder in Open VTB kent de juiste groepen toe aan deze gebruiker als deze
   voor het eerst inlogt.

.. note:: Standaard krijgen deze gebruikers **geen** toegang tot de beheerinterface. Deze
   rechten moeten door een (andere) beheerder :ref:`ingesteld <manual_users>` worden. De
   account is wel aangemaakt.

Providersreferentie
===================

Keycloak
--------

Keycloak is a multi-tenant IDP which itself can configure other IDPs.

To use Keycloak, you need to know your relevant ``realm``. The discovery URL has the form
``https://keycloak.gemeente.nl/auth/realms/${realm}/.well-known/openid-configuration``.
