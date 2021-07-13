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

package ch.renku.acceptancetests.tooling

import cats.syntax.all._
import ch.renku.acceptancetests.model.BaseUrl
import ch.renku.acceptancetests.pages.Page
import org.openqa.selenium.{WebDriver, WebElement}
import org.scalatest.concurrent.Eventually
import org.scalatest.exceptions.TestFailedException
import org.scalatest.exceptions._
import org.scalatestplus.selenium
import org.scalatestplus.selenium.WebBrowser

import scala.concurrent.duration._
import scala.jdk.CollectionConverters._
import scala.language.implicitConversions
import cats.instances.boolean
import java.{util => ju}

trait Grammar extends WebElementOps with Eventually {
  self: WebBrowser with AcceptanceSpec =>

  implicit def toSeleniumPage[Url <: BaseUrl](page: Page[Url])(implicit baseUrl: Url): selenium.Page =
    new selenium.Page {
      override val url = page.url
    }

  object sleep {
    def apply(duration: Duration): Unit = Page SleepThread duration
  }

  object verify {

    def that(element: => WebElement): WebElement = element

    def browserAt[Url <: BaseUrl](page: Page[Url])(implicit baseUrl: Url): Unit = eventually {
      currentUrl.toLowerCase should startWith(page.url.toLowerCase)
      pageTitle            shouldBe page.title
      verifyElementsAreDisplayed(page)
    }

    private def verifyElementsAreDisplayed[Url <: BaseUrl](page: Page[Url]): Unit =
      page.pageReadyElement.map(_.isDisplayed) match {
        case Some(false) => fail(s"'${page.title}' page elements are not displayed")
        case _           => ()
      }

    def browserSwitchedTo[Url <: BaseUrl](page: Page[Url])(implicit baseUrl: Url): Unit = eventually {
      if (webDriver.getWindowHandles.asScala exists forTabWith(page)) ()
      else throw new Exception(s"Cannot find window with ${page.url} and title ${page.title}")
    }

    private def forTabWith[Url <: BaseUrl](page: Page[Url])(handle: String)(implicit baseUrl: Url): Boolean = {
      webDriver.switchTo() window handle
      (currentUrl startsWith page.url) && (pageTitle == page.title)
    }

    def userCanSee(element: => WebElement): Unit = eventually {
      element.isDisplayed shouldBe true
    }
  }

  object reload {

    @scala.annotation.tailrec
    def whenUserCannotSee(findElement: WebDriver => WebElement, attempt: Int = 1): Unit =
      if (
        attempt <= 10 &&
        Either
          .catchOnly[TestFailedException](!findElement(webDriver).isDisplayed)
          .fold(_ => true, identity)
      ) {
        sleep(5 seconds)
        webDriver.navigate().refresh()
        whenUserCannotSee(findElement, attempt + 1)
      } else
        findElement(webDriver).isDisplayed
  }

  def `try few times before giving up`[V](section: WebDriver => V, attempt: Int = 1)(implicit webDriver: WebDriver): V =
    Either.catchOnly[RuntimeException](section(webDriver)) match {
      case Right(successValue)         => successValue
      case Left(error) if attempt > 10 => throw error
      case Left(_) =>
        sleep(5 seconds)
        reloadPage()
        `try few times before giving up`(section, attempt + 1)
    }

  object pause {

    @scala.annotation.tailrec
    def asLongAsBrowserAt[Url <: BaseUrl](page: Page[Url], attempt: Int = 1)(implicit baseUrl: Url): Unit = {
      val maxAttempts   = 120
      val checkInterval = 1 second

      if (attempt <= maxAttempts && (currentUrl startsWith page.url)) {
        sleep(checkInterval)
        asLongAsBrowserAt(page, attempt + 1)
      } else if (attempt > maxAttempts && (currentUrl startsWith page.url))
        fail {
          s"Expected to be redirected from ${page.url} page " +
            s"but gets stuck on $currentUrl for ${(checkInterval * attempt).toSeconds}s"
        }
    }
  }

  def unless(test: Boolean)(testFun: => Any): Unit =
    if (!test) testFun

  protected implicit class WebElementGrammar(element: WebElement) {
    def is(expected:                 String): Unit = element.getText shouldBe expected
    def contains(expected:           String): Unit = element.getText   should include(expected)
    def matches(pattern:             String): Unit = element.getText   should fullyMatch regex pattern
    def hasValue(expected:           String): Unit = element.getAttribute("value") shouldBe expected
    def attributeContains(attribute: String, expected: String): Unit =
      element.getAttribute(attribute) should include(expected)
  }

  protected implicit class OperationOps(unit: Unit) {
    def sleep(duration: Duration): Unit = Page SleepThread duration
  }

  protected implicit def toWebElement(element: WebBrowser.Element): WebElement =
    element.underlying
}
