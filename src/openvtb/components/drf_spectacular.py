from django.utils.translation import gettext_lazy as _

URN_DESCRIPTION = _("""

**URN Pattern**

Open VTB uses URNs (Uniform Resource Names) to link to other resources, below is a description of the pattern that should be used.

**Syntax:**

`urn:<NID>:<NSS>[#<f-component>]`

**Parts:**

- `urn:` (required): fixed prefix for all URNs, every URN must start with this prefix.
- `NID` (required): Namespace Identifier: alphanumeric characters, e.g. `nld`.
- `NSS` (required): Namespace Specific String identifying the object, e.g. `brp:bsn:111222333`.
- `f-component` (optional): Optional component preceded by `#`, e.g. `#section1`.

**Examples:**

`urn:namespace:component:resource:uuid`, `urn:example:foo#bar`

For more information, see the official specification: https://datatracker.ietf.org/doc/html/rfc8141
""")
