# Renku changes


## 0.5.0 (released 2019-11-07)


## Notable improvements

* Enabled search by username and group 🔍
* Fork functionality now allows changing the name 🍴
* Better tools to get information about interactive environments
* Better consistency with project and interactive environment URLs
* Users with developer permissions can now start an interactive environment 🚀

### Miscellaneous
* Commit time is local timezone aware
* Simplified deployment with automatic secrets generation
* Images and project templates now use Renku [0.7.1](https://github.com/SwissDataScienceCenter/renku-python/releases)
* User profile redirects to Keycloak profile

### Features

⭐️ Datasets are now displayed inside a Renku project

### Individual components

For changes to individual components, check:
* renku ui [0.6.4](https://github.com/SwissDataScienceCenter/renku-ui/releases/tag/0.6.4), [0.7.0](https://github.com/SwissDataScienceCenter/renku-ui/releases/tag/0.7.0) and [0.7.1](https://github.com/SwissDataScienceCenter/renku-ui/releases/tag/0.7.1)
* renku-gateway [0.6.0](https://github.com/SwissDataScienceCenter/renku-gateway/releases/tag/0.6.0)
* renku-python [0.7.1](https://github.com/SwissDataScienceCenter/renku-notebooks/releases/tag/0.7.1)
* renku-graph [0.24.3](https://github.com/SwissDataScienceCenter/renku-graph/releases/tag/0.24.3)

## Bug fixes
* Lineage visualization bugs addressed


## Upgrading from 0.4.3
* Update values file according to [the values changelog](https://github.com/SwissDataScienceCenter/renku/blob/master/charts/values.yaml.changelog.md#changes-on-top-of-renku-042)
