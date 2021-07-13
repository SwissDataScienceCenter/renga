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

package ch.renku.acceptancetests.pages

import ch.renku.acceptancetests.model.users.UserCredentials
import org.openqa.selenium.{JavascriptExecutor, WebDriver, WebElement}
import org.scalatestplus.selenium.WebBrowser._

import scala.concurrent.duration._
import scala.language.implicitConversions

object LoginPage
    extends RenkuPage(
      path = "/auth/realms/Renku/protocol/openid-connect/auth",
      title = "Log in to Renku"
    ) {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(logInButton)

  def logInWith(userCredentials: UserCredentials)(implicit webDriver: WebDriver): Unit = eventually {
    usernameField.clear() sleep (1 second)
    usernameField.enterValue(userCredentials.email)

    passwordField.clear() sleep (1 second)
    passwordField.enterValue(userCredentials.password)

    logInButton.click()
  }

  private def usernameField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#username")) getOrElse fail("Username field not found")
  }

  private def passwordField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#password")) getOrElse fail("Password field not found")
  }

  def oidcButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("a.zocial.oidc")) getOrElse fail("OpenIDConnector Button not found")
  }

  private def registerLink(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#kc-registration > span > a")) getOrElse fail("Register link not found")
  }

  def openRegistrationForm(implicit webDriver: WebDriver): Unit = {
    registerLink.click() sleep (5 seconds)

    if (currentUrl contains "/auth/realms/Renku/protocol/openid-connect/auth") {
      // button didn't work, try again
      registerLink.click() sleep (5 seconds)
    }
  }

  def loginSucceeded(implicit webDriver: WebDriver): Boolean = eventually {
    find(cssSelector("#kc-content-wrapper > div.alert.alert-error")) match {
      // If we find the alert, login failed!
      case Some(_) => false
      case None    => true
    }
  }

  def logInButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#kc-login")) getOrElse fail("Log In button not found")
  }
}

/** When a renku instance uses another openID connect provider, the user may get a second login page.
  */
object ProviderLoginPage
    extends RenkuPage(
      path = "/auth/realms/Renku/protocol/openid-connect/auth",
      title = "Log in to Renku"
    ) {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(logInButton)

  def logInWith(userCredentials: UserCredentials)(implicit webDriver: WebDriver): Unit = eventually {
    usernameField.clear() sleep (1 second)
    usernameField.enterValue(userCredentials.email)

    passwordField.clear() sleep (1 second)
    passwordField.enterValue(userCredentials.password)

    logInButton.click()
  }

  def usernameField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#username")) getOrElse fail("Username field not found")
  }

  def passwordField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#password")) getOrElse fail("Password field not found")
  }

  def logInButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#kc-login")) getOrElse fail("Log In button not found")
  }
}

object AuthorizeApplicationPage
    extends GitLabPage(
      path = "/oauth/authorize",
      title = "User Settings · GitLab"
    ) {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(authorizeButton)

  def authorize(implicit webDriver: WebDriver): Unit =
    webDriver.asInstanceOf[JavascriptExecutor].executeScript("arguments[0].click()", authorizeButton)

  def authorizeButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input[data-qa-selector='authorization_button']"))
      .getOrElse(fail("Authorize button not found"))
  }
}

object RegisterNewUserPage
    extends RenkuPage(
      path = "/auth/realms/Renku/login-actions/registration",
      title = "Log in to Renku"
    ) {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(registerButton)

  def registerNewUserWith(userCredentials: UserCredentials)(implicit webDriver: WebDriver): Unit = eventually {
    val nameComps = userCredentials.fullName.split(" ")
    val firstName = nameComps.head
    val lastName  = nameComps.last

    firstNameField.clear() sleep (1 second)
    firstNameField.enterValue(firstName)

    lastNameField.clear() sleep (1 second)
    lastNameField.enterValue(lastName)

    emailField.clear() sleep (1 second)
    emailField.enterValue(userCredentials.email)

    passwordField.clear() sleep (1 seconds)
    passwordField.enterValue(userCredentials.password)

    confirmPasswordField.clear() sleep (1 second)
    confirmPasswordField.enterValue(userCredentials.password)

    registerButton.click()
  }

  def emailField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#email")) getOrElse fail("Email field not found")
  }

  def firstNameField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#firstName")) getOrElse fail("First name field not found")
  }

  def lastNameField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#lastName")) getOrElse fail("Last name field not found")
  }

  def passwordField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#password")) getOrElse fail("Password field not found")
  }

  def confirmPasswordField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#password-confirm")) getOrElse fail("Confirm Password field not found")
  }

  def registerButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#kc-form-buttons > input")) getOrElse fail("Register button not found")
  }
}

case class UpdateAccountInfoPage(userCredentials: UserCredentials)
    extends RenkuPage(
      path = "/auth/realms/Renku/login-actions/first-broker-login",
      title = "Log in to Renku"
    ) {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(submitButton)

  def updateInfo(implicit webDriver: WebDriver): Unit = eventually {
    emailField.clear() sleep (1 second)
    emailField.enterValue(userCredentials.email)

    val nameComps = userCredentials.fullName.split(" ")
    val firstName = nameComps.head
    val lastName  = nameComps.last

    firstNameField.clear() sleep (1 second)
    firstNameField.enterValue(firstName)

    lastNameField.clear() sleep (1 second)
    lastNameField.enterValue(lastName)

    submitButton.click()
  }

  def emailField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#email")) getOrElse fail("Email field not found")
  }

  def firstNameField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#firstName")) getOrElse fail("First name field not found")
  }

  def lastNameField(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("input#lastName")) getOrElse fail("Last name field not found")
  }

  def submitButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#kc-form-buttons > input")) getOrElse fail("Submit button not found")
  }
}
