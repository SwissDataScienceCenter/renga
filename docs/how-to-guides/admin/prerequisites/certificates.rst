.. _certificates:

Certificates
============

To enable HTTPS on the Renku website you need valid certificates for the ingress.

This can be achieved by either deploying a certificate issuer like LetsEncrypt or creating certificates manually and inserting them as Kubernetes secrets.

LetsEncrypt
------------------

If you have installed Helm you can deploy `LetsEncrypt <https://letsencrypt.org/>`_.

The following are steps to install LetsEncrypt using Helm.
To run the following commands you can use the `cert-manager-values.yaml <https://github.com/SwissDataScienceCenter/renku-admin-docs/blob/master/helm-installs/cert-manager-values.yaml>`_ and `cert-manager-issuer.yaml <https://github.com/SwissDataScienceCenter/renku-admin-docs/blob/master/manifests/cert-manager-issuer.yaml>`_ files.
Make sure to edit the cert-manager-issuer.yaml file and fill in the correct `email` field.

.. code-block:: console

   $ helm install cert-manager jetstack/cert-manager -f helm-installs/cert-manager-values.yaml --namespace kube-system
   $ kubectl apply -f manifests/cert-manager-issuer.yaml

Now you can check that certificates can be issued automatically using a test deployment.
For more information, please check `LetsEncrypt cert-manager Helm documentation <https://hub.helm.sh/charts/jetstack/cert-manager>`_

Generate manually
--------------------

You can also use an SSL certificate issued by another certificate authority.
Add the mentioned certificate as a secret to the ``renku`` namespace.

.. code-block:: console

  $ kubectl -n renku create secret tls renku-tls --cert=certificate.crt --key=certificate.key

If GitLab is deployed as part of Renku you also need a certificate for the registry, this can be included in the ``.crt`` file.
