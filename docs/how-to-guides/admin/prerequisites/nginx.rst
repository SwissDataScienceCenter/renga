.. _nginx:

NGINX ingress
============================

Renku provides some `kubernetes services <https://kubernetes.io/docs/concepts/services-networking/service/>`_ that need to be exposed. Traffic in Kubernetes can be managed and controlled using different tools.
The setup of Renku assumes that `NGINX Ingress <https://www.nginx.com/products/nginx/kubernetes-ingress-controller/>`_ is deployed and running in the cluster.

Install the `ingress-nginx`:

Copy the content of this into a file named ``nginx-values.yaml``

.. code-block:: bash

    controller:
      kind: DaemonSet
      service:
        externalTrafficPolicy: Local
        nodePorts:
          http: 32080
          https: 32443
        type: NodePort
    rbac:
      create: true

.. code-block:: bash

   $ helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   $ helm repo update
   $ helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx -f nginx-values.yaml  --set controller.hostNetwork=true

Verify that the deployment works as expected:

.. code-block:: bash

  $ helm status ingress-nginx --namespace ingress-nginx | grep -i port

The output of the previous command should be:

.. code-block:: bash

    export HTTP_NODE_PORT=32080
    export HTTPS_NODE_PORT=32443
    export NODE_IP=$(kubectl --namespace ingress-nginx get nodes -o jsonpath="{.items[0].status.addresses[1].address}")
    echo "Visit http://$NODE_IP:$HTTP_NODE_PORT to access your application via HTTP."
    echo "Visit https://$NODE_IP:$HTTPS_NODE_PORT to access your application via HTTPS."
                  servicePort: 80

Now let's check that we can contact the ingress:

.. code-block:: bash

  $ curl -v http://<floating-ip>/
  default backend - 404
