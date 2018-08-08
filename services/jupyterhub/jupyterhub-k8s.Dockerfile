FROM jupyterhub/k8s-hub:8c0aeef

USER root

COPY requirements-k8s.txt /tmp/requirements.renku.txt
RUN pip3 install -r /tmp/requirements.renku.txt --no-cache-dir

COPY spawners.py /usr/local/lib/python3.6/dist-packages/

USER ${NB_USER}
