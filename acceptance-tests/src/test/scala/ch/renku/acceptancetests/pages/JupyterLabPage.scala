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

import ch.renku.acceptancetests.model.projects.ProjectIdentifier
import org.openqa.selenium.Keys.RETURN
import org.openqa.selenium.interactions.Actions
import org.openqa.selenium.{WebDriver, WebElement}
import org.scalatestplus.selenium.WebBrowser.{cssSelector, find}

object JupyterLabPage {

  def apply()(implicit projectPage: ProjectPage): JupyterLabPage =
    new JupyterLabPage(projectPage.projectSlug, projectPage.namespace)

  def apply(projectId: ProjectIdentifier): JupyterLabPage =
    new JupyterLabPage(projectId.slug, projectId.namespace)
}

class JupyterLabPage(projectSlug: String, namespace: String)
    extends RenkuPage(
      path = s"/sessions/$projectSlug",
      title = "JupyterLab"
    ) {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(terminalIcon)

  def terminalIcon(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("div.jp-LauncherCard [data-icon='ui-components:terminal']")) getOrElse fail(
      "Terminal icon not found"
    )
  }

  object terminal {

    def %>(command: String)(implicit webDriver: WebDriver): Unit = eventually {
      val terminalElement =
        find(cssSelector("#jp-Terminal-0 > div > div.xterm-screen > canvas.xterm-cursor-layer")) getOrElse fail(
          "Terminal not found"
        )

      new Actions(webDriver)
        .moveToElement(terminalElement)
        .click()
        .sendKeys(s"$command$RETURN")
        .build()
        .perform()
    }
  }
}
