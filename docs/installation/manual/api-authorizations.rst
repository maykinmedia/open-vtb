.. _manual_api_auth:

=====================
API access management
=====================

The APIs offered by Open VTB are not accessible
without authentication and authorization, data is properly secured.

Before an application can request, enter, edit, or delete data, it must be known and authorized to do so.

.. _manual_generate_token:

Generating a token for API access
=================================

You can access the application for which you wish to set authorizations via the
Open VTB management environment. Within the management environment, under
the **Users** menu option, you will find the **Tokens** link. This link leads to a list view
of all created Tokens that allow access to the Open VTB APIs.


To create a new token, the user clicks on the **ADD TOKEN** button.
Here, a user can be selected to whom the token is linked.
Finally, when the **Save** button is clicked, a token is generated
and displayed on the screen to which the user is redirected.

.. _manual_use_oidc:

Using a JWT token from an OIDC provider for API access
======================================================

After OpenID Connect is :ref:`configured <manual_oidc>`,
JWT tokens from the OpenID provider can be used to access the API.


