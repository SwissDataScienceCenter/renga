.. _standalone-keycloak:

Stand-alone Keycloak: Renku configuration
=========================================

If you have your own Keycloak instance that you want to use for authentication with Renku you need to:

- Create a Realm named Renku
- Setup the preferred parameters regarding user registration, token lifetime and activation of OTP.
- Import the four clients from their respective json files in the `keycloak-standalone-clients <https://github.com/SwissDataScienceCenter/renku-admin-docs/blob/master/keycloak-standalone-clients>`_ folder after filling in the correct domain. **Note.** if you also have a standalone GitLab instance you should fill in the proper URIs in the gitlab.json file.
- For the GitLab client copy the secret from the Credentials tab and paste it at the dedicated place in renku-values.yaml.
- Same as above for gateway client.
