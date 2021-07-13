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

import ch.renku.acceptancetests.model.projects.ProjectDetails
import ch.renku.acceptancetests.model.projects.ProjectDetails._
import ch.renku.acceptancetests.model.users.UserCredentials
import org.openqa.selenium.{WebDriver, WebElement}
import org.scalatestplus.selenium.WebBrowser
import org.scalatestplus.selenium.WebBrowser.{cssSelector, find, findAll}

case object ProjectsPage
    extends RenkuPage(
      path = "/projects",
      title = "Renku"
    )
    with TopBar {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(YourProjects.tab)

  object YourProjects {

    def tab(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("#link-projects-your")) getOrElse fail("Projects -> Your Projects tab not found")
    }

    def searchField(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("#searchQuery")) getOrElse fail("Projects -> Filter by project field not found")
    }

    def searchButton(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("#searchButton")) getOrElse fail("Projects -> Search button not found")
    }

    def linkTo(
        project:          ProjectDetails
    )(implicit webDriver: WebDriver, userCredentials: UserCredentials): WebElement =
      maybeLinkTo(project) getOrElse fail(s"'${project.title}' not found")

    def maybeLinkTo(
        project:          ProjectDetails
    )(implicit webDriver: WebDriver, userCredentials: UserCredentials): Option[WebElement] = eventually {
      find(cssSelector(s"a[href='/projects/${userCredentials.userNamespace}/${project.title.toPathSegment}']"))
    }

    /** Return all the project links.
      */
    def projectLinks(implicit webDriver: WebDriver): List[WebBrowser.Element] = findAll(
      cssSelector(
        "main > div:nth-child(4) > div > div:nth-child(3) > div > div > div.d-flex.flex-fill.flex-column.ml-2.mw-0.flex-sm-row > div.d-flex.flex-column.text-truncate > p:nth-child(1) > b > a"
      )
    ) toList
  }
}
