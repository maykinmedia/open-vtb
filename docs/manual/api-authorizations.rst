.. _manual_api_auth:

=====================
API access management
=====================

The APIs offered by **Open VTB** are not accessible
without authentication and authorization, data is properly secured.
Before an application can request, enter, edit, or delete data, it must be known and authorized to do so.

This page explains how to use both API tokens and JWT tokens from an OIDC Connect to access the Open VTB APIs.

.. _manual_use_token:

Using an API Token
==================

API tokens can be generated via the **Open VTB admin** interface and are tied to a specific user, see :ref:`configuration <configure_api_token>`

We can now make an HTTP request to one of the APIs of Open VTB.
For this example, we have used `curl`_ to make the request.

.. code-block:: bash

   curl --request GET \
   --header 'Authorization: Token {{ token }}' \
   {{ API_URL }}

The API will validate the token and grant access according to the permissions of the associated user.

.. _manual_use_oidc:

Using a JWT Token from an OIDC Connect
======================================

After OpenID Connect is :ref:`configured <configure_openid_connect_token>`, JWT tokens from the OpenID provider can be used to access the API.
This configuration can be performed either through the admin interface or via the setup configuration,
see :ref:`Admin OIDC Configuration Step  <ref_step_mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep>`.

To obtain an access token using the *client credentials* flow, run the following command:

.. code-block:: bash

    curl --request POST \
      --url "{{ token_url }}" \
      --header "Content-Type: application/x-www-form-urlencoded" \
      --data "client_id={{ client_id }}" \
      --data "client_secret={{ client_secret }}" \
      --data "grant_type=client_credentials" \
      --data "scope=openid"


Once the access token has been generated, you can use it to call the API as follows:

.. code-block:: bash

    curl --request GET \
      --header "Authorization: Bearer {{ access_token }}" \
      {{ API_URL }}


.. _Curl: https://curl.se/docs/manpage.html
