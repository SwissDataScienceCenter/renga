/*
 * Copyright 2021 Swiss Data Science Center (SDSC)
 * A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
 * Eidgenössische Technische Hochschule Zürich (ETHZ).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ch.renku.acceptancetests.workflows

import ch.renku.acceptancetests.pages._
import ch.renku.acceptancetests.tooling.AcceptanceSpec
import ch.renku.acceptancetests.workflows.LoginType._

import scala.concurrent.duration._
import scala.language.postfixOps

trait Login {
  self: AcceptanceSpec =>

  def `log in to Renku`: LoginType = {
    Given("user is not logged in")
    go to LandingPage sleep (1 second)
    verify browserAt LandingPage

    When("user clicks on the Login button")
    // Wait for the page to update
    sleep(2 seconds)
    click on LandingPage.loginButton
    Then("they should get into the Login Page")
    verify browserAt LoginPage

    val loginType = if (userCredentials.useProvider) {
      logIntoRenkuUsingProvider
    } else {
      logIntoRenkuDirectly
    }

    Then("they should get into the Welcome page")
    verify browserAt WelcomePage

    loginType
  }

  private def logIntoRenkuUsingProvider: LoginType = {
    When("user clicks on the provider login page")
    val providerLoginPage = LoginPage openProviderLoginPage

    And("enters credentials and logs in")
    providerLoginPage logInWith userCredentials

    val authorizationPage = LoginPage.AuthorizeApplicationPage()
    if (currentUrl startsWith authorizationPage.url) {
      And("authorizes the application")
      authorizationPage authorize;
      // It may be necessary to authorize twice
      if (currentUrl startsWith authorizationPage.url) {
        And("authorizes the application a second time")
        authorizationPage authorize
      }
    }

    // This is a first login, and we need to provide account information
    if (currentUrl contains "login-actions/first-broker-login") {
      val updateInfoPage = LoginPage.UpdateAccountInfoPage(userCredentials)
      And("updates user information")
      updateInfoPage.updateInfo sleep (5 seconds)
    }

    // Authorization may come later
    if (currentUrl startsWith authorizationPage.url) {
      And("authorizes the application")
      authorizationPage authorize;
      // It may be necessary to authorize twice
      if (currentUrl startsWith authorizationPage.url) {
        And("authorizes the application a second time")
        authorizationPage authorize
      }
    }
    LoginWithProvider
  }

  private def logIntoRenkuDirectly: LoginType = {
    When("user enters credentials and logs in")
    LoginPage logInWith userCredentials

    if (LoginPage loginSucceeded) {
      val providerLoginPage = LoginPage.ProviderLoginPage()
      val lt = if (currentUrl startsWith providerLoginPage.url) {
        And("enters information with the provider")
        providerLoginPage logInWith userCredentials
        LoginWithProvider
      } else LoginWithoutProvider
      val authorizationPage = LoginPage.AuthorizeApplicationPage()
      if (currentUrl startsWith authorizationPage.url) {
        And("authorizes the application")
        authorizationPage authorize;
        // It may be necessary to authorize twice
        if (currentUrl startsWith authorizationPage.url) {
          And("authorizes the application a second time")
          authorizationPage authorize
        }
      }
      lt
    } else {
      if (userCredentials.register) {
        And("login fails")
        Then("try to register the user")
        registerNewUserWithRenku
      } else fail("Incorrect user credentials.")
    }
  }

  private def registerNewUserWithRenku: LoginType = {
    When("user opens registration form")
    val lt = LoginPage openRegistrationForm;

    And("registers")
    val registerPage = LoginPage.RegisterNewUserPage()
    registerPage registerNewUserWith userCredentials

    And("logs into provider")
    val providerLoginPage = LoginPage.ProviderLoginPage()
    providerLoginPage logInWith userCredentials

    val authorizationPage = LoginPage.AuthorizeApplicationPage()
    if (currentUrl startsWith authorizationPage.url) {
      And("authorizes the application")
      authorizationPage authorize;
      // It may be necessary to authorize twice
      if (currentUrl startsWith authorizationPage.url) {
        And("authorizes the application a second time")
        authorizationPage authorize
      }
    }
    lt
  }

  def `log out of Renku`(implicit loginType: LoginType): Unit = {
    When("user clicks the Log out link")
    click on WelcomePage.TopBar.topRightDropDown
    click on WelcomePage.TopBar.logoutLink

    unless(loginType == LoginWithProvider) {
      Then("they should get back into the Landing page")
      verify browserAt LandingPage
      verify userCanSee LandingPage.loginButton sleep (1 second)
    }
  }
}

sealed trait LoginType

object LoginType {
  case object LoginWithProvider    extends LoginType
  case object LoginWithoutProvider extends LoginType
}
