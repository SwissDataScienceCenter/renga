.. _admin_privacycookie:

Configuring privacy page and cookie banner
------------------------------------------

Privacy page
~~~~~~~~~~~~

The UI has a privacy page with a completely configurable content, suited for showing
any policy/terms related information, like the `Privacy Policy Statement` or the
`Terms of Use`.

The content is read from a ``ConfigMap``. You need to configure the values in
``ui.privacy.page`` to enable the feature and set the reference ConfigMap name and key.
Both ``ui.privacy.enabled`` and ``ui.privacy.page.enabled`` need to be ``true`` for
enabling the privacy page.

.. note::

  If you don't set the ConfigMap name and key,
  `a sample <https://github.com/SwissDataScienceCenter/renku-ui/blob/master/helm-chart/renku-ui/templates/configmap.yaml>`_
  will be used instead. You can start from it as a template to create your customized ConfigMap.

The `Markdown syntax <https://en.wikipedia.org/wiki/Markdown>`_ is fully supported for the
privacy page content.

Cookie banner
~~~~~~~~~~~~~

Since RenkuLab requires user identification and implements a login system, cookies are
required at all levels to provide basic functionality. Please mind that cookies are also used
for anonymous users (i.e. without an account or not currently logged in). To comply with
international laws, it's strongly advised to explicitly require consent to the user for storing
these data and using cookies.

To activate this feature, please set ``ui.privacy.enabled: true``. We have already configured a
default cookie banner to inform the users about the aforementioned requirements and points to
point them to the privacy page for further details.

It's possible to customize the banner to your own needs, changing both the appearance and the
content. We use `cookie consent <https://github.com/Mastermindzh/react-cookie-consent>`_ to
create the banner and we support customization of all the properties exposed by the library.
All the adjustments should be provided as values in ``ui.privacy.banner`` as follows:

1. ``content``: The HTML content of the cookie banner. Please mind that links should point
   to local content. Use the privacy page to add references to third party sites.
2. ``layout``: The list of properties for the cookies consent plugin. We use
   `Bootstrap <https://getbootstrap.com/docs>`_ for the UI, therefore all the Bootstrap
   classes can be used to customize the appearance.

You can refer to the current
`values.yaml in the renku-ui repository <https://github.com/SwissDataScienceCenter/renku-ui/blob/master/helm-chart/renku-ui/values.yaml>`_
to check the default values and to find an example of how to apply different settings.
