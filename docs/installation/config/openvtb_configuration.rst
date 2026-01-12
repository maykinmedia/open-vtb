.. _installation_configuration:

==============================
Open VTB configuration (admin)
==============================

Before you can work with Open VTB after installation, a few settings need to be
configured first.

.. note::

    This document describes the manual configuration via the admin.

.. _configure_api_token:

Configure an API Token
======================

You can access the application for which you want to configure authorizations through the **Open VTB admin** interface.
In the admin, go to **API Autorisaties** > **Tokens**.
This page shows a list of all existing tokens that provide access to the Open VTB APIs.

To create a new token:

1. Click **Add Token** / **Token toevoegen** in the top right.
2. Select the **User** for whom the token should be created.
3. Click **Save** / **Opslaan** at the bottom.


Once the token is created, the system redirects you to a page where the generated token is displayed.
The token key also appears in the list view and can be used in the ``Authorization`` header when performing API calls.
See :ref:`manual_use_token` for instructions on how to use the token in API requests.

.. _configure_openid_connect_token:

Configure OpenID Connect
========================

Navigate to **Accounts** > **OIDC Providers**.

1. Click **Add OIDC Provider** / **OIDC Provider toevoegen**.
2. Fill in the fields required for the provider you want to use. See :ref:`manual_oidc`.
3. Click **Save** / **Opslaan** in the bottom left.

Next, navigate to **Accounts** > **OIDC Clients**.

1. Select the **admin-oidc** client.
2. Choose the **provider** you set up earlier.
3. Fill in the fields required for the client.
4. Enable the configuration.
5. Click **Save** / **Opslaan** in the bottom left.

.. note::

    In addition to configuring the **admin-oidc** client for the admin interface,
    you must also configure the client with the identifier **api-oidc** to enable OpenID Connect authentication for the API.

1. Select the **api-oidc** client.
2. Choose the **provider** you set up earlier.
3. Fill in the fields required for the client.
4. Enable the configuration.
5. Click **Save** / **Opslaan** in the bottom left.

This makes it explicit that:

* `admin-oidc` is for the admin UI
* `api-oidc` is required for API authentication via OIDC

After OpenID Connect is :ref:`configured <manual_oidc>`, JWT tokens from the OpenID provider
can be used to access the API. JWT tokens from the OpenID Connect can be used to access the API:
see :ref:`manual_use_oidc` for how to obtain and use the JWT token in API requests.

This configuration can be performed either through the admin interface
or via the setup configuration. See :ref:`Admin OIDC Configuration Step <ref_step_mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep>`.
