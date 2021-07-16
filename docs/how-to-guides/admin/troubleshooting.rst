.. _admin_troubleshooting:

Troubleshooting a Renku deployment
=========================================

Gateway in a CrashLoopBackOff state
------------------------------------

If the gateway pod is in a CrashLoopBackOff state, it means that it could not
contact keycloak. Please verify that keycloak is reachable and that the
configuration values for the gateway are correct.
