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

import ch.renku.acceptancetests.pages.LoginPage.oidcButton
import ch.renku.acceptancetests.pages._
import ch.renku.acceptancetests.tooling.AcceptanceSpec
import ch.renku.acceptancetests.workflows.LoginType._

import scala.annotation.tailrec
import scala.concurrent.duration._

trait Login {
  self: AcceptanceSpec =>

  private var maybeLoginType: Option[LoginType] = None

  def `log in to Renku`: Unit = {

    Given("user is not logged in")

    `try few times before giving up` { _ =>
      go to LandingPage sleep (2 seconds)
      verify browserAt LandingPage
    }

    When("user clicks on the Login button")
    // Wait for the page to update
    sleep(2 seconds)
    click on LandingPage.loginButton
    Then("they should get into the Login Page")

    maybeLoginType = Some {
      if (userCredentials.useProvider) `log in to Renku using provider`
      else `log in to Renku directly`
    }

    Then("they should get into the Welcome page")
    verify browserAt WelcomePage
  }

  def `log out of Renku`: Unit = {
    sleep(3 seconds)
    When("user clicks the profile button")
    WelcomePage.TopBar.clickOnTopRightDropDown sleep (1 second)
    When("user clicks the Log out link")
    click on WelcomePage.TopBar.logoutLink sleep (3 seconds)

    unless(maybeLoginType contains LoginWithProvider) {
      Then("they should get back into the Landing page")
      verify browserAt LandingPage
      verify userCanSee LandingPage.loginButton sleep (1 second)
    }
  }

  private def `log in to Renku using provider`: LoginType = {
    When("user clicks on the provider login page")
    LoginPage.oidcButton.click() sleep (5 seconds)

    if (!(currentUrl contains ProviderLoginPage.path)) {
      println("Not on OpenID login provider page, trying again")
      oidcButton.click() sleep (5 seconds)
    }

    And("enters credentials and logs in")
    ProviderLoginPage logInWith userCredentials

    `authorize application if necessary`()

    // This is a first login, and we need to provide account information
    if (currentUrl contains "login-actions/first-broker-login") {
      And("updates user information")
      UpdateAccountInfoPage(userCredentials).updateInfo sleep (5 seconds)
    }

    // Authorization may come later
    `authorize application if necessary`()

    LoginWithProvider
  }

  private def `log in to Renku directly`: LoginType = {
    When("user enters credentials and logs in")
    LoginPage logInWith userCredentials

    if (LoginPage loginSucceeded) {
      val loginType =
        if (currentUrl contains ProviderLoginPage.path) {
          And("enters information with the provider")
          ProviderLoginPage logInWith userCredentials
          LoginWithProvider
        } else LoginWithoutProvider

      `authorize application if necessary`()

      loginType
    } else {
      if (userCredentials.register) {
        And("login fails")
        Then("try to register the user")
        `register new user with Renku`
      } else fail("Incorrect user credentials.")
    }
  }

  private def `register new user with Renku`: LoginType = {
    When("user opens registration form")
    LoginPage openRegistrationForm;

    And("registers")
    RegisterNewUserPage registerNewUserWith userCredentials

    And("logs into provider")
    ProviderLoginPage logInWith userCredentials

    `authorize application if necessary`()

    LoginWithProvider
  }

  @tailrec
  private def `authorize application if necessary`(attempt: String = "first"): Unit =
    if (currentUrl startsWith AuthorizeApplicationPage.url) {
      And(s"authorizes the application for the $attempt time")
      AuthorizeApplicationPage authorize

      // It may be necessary to authorize twice
      `authorize application if necessary`(attempt = "second")
    }
}

sealed trait LoginType

object LoginType {
  case object LoginWithProvider    extends LoginType
  case object LoginWithoutProvider extends LoginType
}
