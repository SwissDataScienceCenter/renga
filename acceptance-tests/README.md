# renku-acceptance-tests

This project contains Renku acceptance tests.

There are several acceptance tests, which are all in the ch.renku.acceptancetests package.

| Class Name                | Purpose                                                          |
| ------------------------- | ---------------------------------------------------------------- |
| LoginSpec                 | Just check that login/logout works                               |
| MinimalFunctionalitySpec  | Check that the basic features are working                        |
| HandsOnSpec               | Run through the hands-on tutorial                                |
| ExistingProjectSpec       | Not normally run, but useful for debugging/developing            |

Some tests create new projects (MinimalFunctionalitySpec, HandsOnSpec). In these cases, the project name is
normally of the form `test_[timestamp]`. This makes it easy to identify the test projects and generally avoid
name collisions. If the test runs successfully to completion, the project is deleted at the end of the test.
If the test fails, then the project is left around to aid debugging.

## Running on Docker

The easiest way to run the tests is to use docker/docker-compose.

### Installation

The `docker-compose` command has to be available: it is easiest to install it with `pip`.

### Running

To run through docker-compose, the tests parameters need to be provided as environment variables:

```
docker-compose run \
-e RENKU_TEST_URL=https://kuba.dev.renku.ch \
-e GITLAB_TEST_URL=https://kuba.dev.renku.ch/gitlab \
-e RENKU_TEST_FULL_NAME="<full user name>" \
-e RENKU_TEST_EMAIL=<email> \
-e RENKU_TEST_USERNAME=<username> \
-e RENKU_TEST_PASSWORD=<password> \
sbt
```

By default, all tests are run. You can provide an argument to run a specific test:
```
docker-compose run \
-e RENKU_TEST_URL=https://kuba.dev.renku.ch \
-e GITLAB_TEST_URL=https://kuba.dev.renku.ch/gitlab \
-e RENKU_TEST_FULL_NAME="<full user name>" \
-e RENKU_TEST_EMAIL=<email> \
-e RENKU_TEST_USERNAME=<username> \
-e RENKU_TEST_PASSWORD=<password> \
sbt *<test-class-name>*
```
__**IMPORTANT**__

Once you do changes to the `Dockerfile` do not forget to build the image with `docker-compose build`.

## Running through Helm test

The `helm test` command can also be used to execute the tests against a Helm release of Renku.

When testing a Renku release that relies on an external GitLab instance, the test user must already
have an existing account on that GitLab instance with login credentials specified in the
values.yaml file. Note that the same user (with the same username/password combination!) must also exist in the Keycloak instance which is part of the Renku release being tested. Alternatively, if the `.Values.tests.registerTestUser` is set to `true`, the test suit will try to register a new user with the provided details.
In case of failing tests an archive with the test results is produced and can be -optionally- pushed to a S3 bucket. The
parameters to use the S3 bucket needs to be provided in the `values.yaml` file.
```yaml
tests:
  ## User account for running `helm test`
  parameters:
    username: foo.bar
    fullname: Foo Bar
    email: foo.bar@example.com
    password: FooBar
  resultsS3:
    host:
    bucket:
    filename:
    accessKey:
    secretKey:
```
The tests can now be executed:
```bash
helm --namespace renku-foo test renku-foo --logs
```

The acceptance tests will run on the Kubernetes cluster where `renku-foo` is deployed, in the
same namespace, in a pod named `renku-foo-acceptance-tests`. Once the tests are completed
(successfully or otherwise) the container is terminated.

## Running using sbt

### Installation

In order to run the tests you need to install:
* Java Development Kit (JDK) >= 8 (see: https://adoptopenjdk.net/?variant=openjdk11&jvmVariant=openj9)
* sbt >= 1.3.3 (use `sbt sbtVersion` to verify current version but run it not from the project root)
  * Mac users: `brew install sbt`
  * Linux users see: https://www.scala-sbt.org/1.x/docs/Installing-sbt-on-Linux.html
* chromedriver
  * Mac users: `brew tap homebrew/cask && brew install --cask chromedriverr`
  * Debian based users: `sudo apt-get install chromium-chromedriver`
  * for other see: https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver
* Python 3, pip and the following packages which can be installed using `python3 -m pip install '<package-name>==<version>'`:
  * papermill < 1.2.0
  * requests >= 2.20.0
  * jupyterhub = 1.1.0
  * nbresuse = 0.3.3
  * jupyterlab-git = 0.20.0
  * pipx >= 0.15.0.0

### Running

The tests are run by executing `sbt` in the project's root.

In order to run the acceptance tests, it is necessary to provide information for reaching and logging into the
Renku instance. These parameters can be provided either as command-line arguments (using
`-D<argument>=<value>`), environment variables or put into the `tests-defaults.conf` file. The precedence
order is command-line argument, environment variable and the defaults file.


To create a `tests-defaults.conf` file, copy the `tests-defaults.conf.template` file and fill in the values.

| Argument          | Environment                    | Purpose                                                                                                                                                                                                                                                |
| ----------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| env               | RENKU_TEST_URL                 | URL to a Renku server, e.g., https://dev.renku.ch                                                                                                                                                                                                      |
| cliVersion        | RENKU_CLI_VERSION              | the version of Renku CLI the tests should use; read from the renku API if not specified                                                                                                                                                                |
| gitLabUrl         | GITLAB_TEST_URL                | URL to a GitLab server, e.g., https://dev.renku.ch/gitlab; defaulted to env/gitlab if not specified                                                                                                                                                    |
| email             | RENKU_TEST_EMAIL               | user's email e.g. `jakub.chrobasik@epfl.ch`                                                                                                                                                                                                            |
| username          | RENKU_TEST_USERNAME            | user's username e.g. `jakub.chrobasik1`                                                                                                                                                                                                                |
| fullname          | RENKU_TEST_FULL_NAME           | user's full name e.g. `Jakub Józef Chrobasik`                                                                                                                                                                                                          |
| password          | RENKU_TEST_PASSWORD            | user's password                                                                                                                                                                                                                                        |
| gitlabaccesstoken | RENKU_TEST_GITLAB_ACCESS_TOKEN | user's personal access token in GitLab with `api`, `read_api`, `read_repository`, `write_repository` scopes (optional - if missing credentials are used to obtain an oauth token which requires the given `username` and `password` to work on GitLab) |
| provider          | RENKU_TEST_PROVIDER            | if non-empty, use an OpenID provider for auth                                                                                                                                                                                                          |
| register          | RENKU_TEST_REGISTER            | if non-empty, register a new user; has precedence over provider                                                                                                                                                                                        |
| docsrun           | RENKU_TEST_DOCS_RUN            | if non-empty, screenshot for docs during hands-on test                                                                                                                                                                                                 |
| extant            | RENKU_TEST_EXTANT_PROJECT      | if non-empty, an existing project to use for tests                                                                                                                                                                                                     |
| anon              | RENKU_TEST_ANON_PROJECT        | namespace/name for the project to test anonymously                                                                                                                                                                                                     |
| anonAvail         | RENKU_TEST_ANON_AVAILABLE      | if true, anonymous environments will be tested.                                                                                                                                                                                                        |
| batchRem          | RENKU_TEST_BATCH_REMOVE        | if true, run the BatchRemoveProjectSpec                                                                                                                                                                                                                |
| remPattern        | RENKU_TEST_REMOVE_PATTERN      | pattern to match to decide if a project should be batch removed                                                                                                                                                                                        |

For example, the following may be run in the project's root: `sbt -Denv=https://renku-kuba.dev.renku.ch
-Demail=<email> -Dusername=<username> -Dfullname='<full user name>' -Dpassword=<password> test`

In the case there's a need of running a single test the `test` part should be replaced with `"testOnly
*<test-class-name>*"`.

On some machines, providing values with spaces using `-D` causes sbt to complain `Could not find or load main
class`. In this case, the environment variables should be used to provide the values.


__**NOTICE**__

* When running locally, it's very important that version of your Chrome matches the version of the chromedriver.
If these versions does not match you have to upgrade one or the other and *reopen* the browser. Running with
Docker avoids this problem.
* There's a `tests-execution.log` file created in the `target` directory of the tests where `DEBUG` log statements generated during tests execution are written. This information might be useful when investigating tests failures.

## Running in console

For development, it can be nice to try things out on the console. For this, get started by running the
following:


```bash
sbt test:console
```

Once the console is up, execute the following to import the libraries for working with Selenium:

```
:load src/test/scala/ch/renku/acceptancetests/ReplShell.scala
```

Then, on the console, you can execute statements like:

```scala
val webDriver = ReplShell.getChromeWebDriver("https://dev.renku.ch")
val loginButtons = webDriver.findElements(By.cssSelector("a[href='/login']"))
```

# Development

You can work on the tests using editor of your choice but using either Intellij or VS Code could make your
life by far simpler. In both cases you need a Scala plugin installed into your IDE. In case of the VS Code
there's a Scalameta plugin which can be installed from
https://marketplace.visualstudio.com/items?itemName=scalameta.metals.


Please use the `scalameta.metals` as a default formatter for the scala sources and **I strongly encourage to
click the `Format on save` feature**.


The test are built using the Page Object Pattern (e.g.
https://www.pluralsight.com/guides/getting-started-with-page-object-pattern-for-your-selenium-tests) which in
short is about wrapping an UI page into a class/object and using it in the test script.


As mentioned above there's a `target/tests-execution.log` file where tests debug statements from tests execution are written.

## Project organization

All the interesting parts are located in the `src/test/scala/ch/renku/acceptancetests` folder which can be
perceived as a tests classes root folder. The test scenarios are suffixed with `Spec` while all the page
objects are put into the `pages` subfolder.


# FAQ

* Q: I'm getting `Error: Could not find or load main class`

  A: Please verify version of sbt in your computer using `sbt sbtVersion` but run it not from the project root.


* Q:  `value seconds is not a member of Int`

  A:

  ```
  import scala.concurrent.duration._
  ```

* Q:
  ```
  type mismatch;
   found   : String("Parent Group")
   required: eu.timepit.refined.api.Refined[String,eu.timepit.refined.collection.NonEmpty]
  ```

  A:
  ```
  import eu.timepit.refined.auto._
  ```
