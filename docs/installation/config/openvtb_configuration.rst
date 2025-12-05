.. _installation_configuration:

==============================
Open VTB configuration (admin)
==============================

Before you can work with Open VTB after installation, a few settings need to be
configured first.

.. note::

    This document describes the manual configuration via the admin.

.. _installation_configuration_sites:

Create an API token
===================

Open VTB
--------
By creating an API token, we can perform an API test call to verify the successful
installation.

Navigate to **API Autorisaties** > **Tokens** and click on **Token toevoegen**
in the top right.

1. Select the user you want to create a token for
2. Click **Opslaan** in the bottom left

After creating the **Token** the **key** is shown in the list page. This value
can be used in the ``Authorization`` header.


Making an API call
------------------

We can now make an HTTP request to one of the APIs of Open VTB. For this
example, we have used `curl`_ to make the request.

.. code-block:: bash

   curl --request GET \
   --header 'Authorization: Token {{ token }}' \
   --header 'Content-Type: application/json' \
   {{ API_URL }}

.. _Curl: https://curl.se/docs/manpage.html

Configure OpenID Connect
========================

Open VTB
--------

Navigate to **Config** > **OpenID**.

1. Fill in the fields required for the provider you want to use. See :ref:`manual_oidc`.
2. Enable the configuration.
3. Click **Opslaan** in the bottom left

Making an API call
------------------

We can now make an HTTP request to one of the APIs of Open VTB. For this
example, we have used `curl`_ to make the request.

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
      --header "Content-Type: application/json" \
      {{ API_URL }}


.. _Curl: https://curl.se/docs/manpage.html
