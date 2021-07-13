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

import ch.renku.acceptancetests.workflows.Environments
import org.openqa.selenium.WebDriver
import org.openqa.selenium.chrome.{ChromeDriver, ChromeDriverService, ChromeOptions}
import org.scalatest._
import org.scalatest.featurespec.AnyFeatureSpec
import org.scalatest.matchers.should
import org.scalatestplus.selenium.WebBrowser

trait AcceptanceSpec
    extends AnyFeatureSpec
    with BddWording
    with BeforeAndAfterAll
    with should.Matchers
    with WebBrowser
    with Environments
    with Grammar
    with GitLabApi
    with RenkuApi
    with ScreenCapturingSpec
    with AcceptanceSpecData
    with AcceptanceSpecPatience {

  protected implicit val browser: AcceptanceSpec = this

  implicit lazy val webDriver: WebDriver = startWebDriver

  protected implicit val docsScreenshots: DocsScreenshots = DocsScreenshots(this, webDriver)

  protected override def afterAll(): Unit = {
    webDriver.quit()
    super.afterAll()
  }

  private def startWebDriver: WebDriver =
    sys.env.get("DOCKER") match {
      case Some(_) =>
        new ChromeDriver(
          new ChromeDriverService.Builder().withWhitelistedIps("127.0.0.1").build,
          new ChromeOptions().addArguments("--no-sandbox", "--headless", "--disable-gpu", "--window-size=1920,1400")
        )
      case None =>
        new ChromeDriver(
          new ChromeOptions().addArguments("--window-size=1920,1400")
        )
    }
}
