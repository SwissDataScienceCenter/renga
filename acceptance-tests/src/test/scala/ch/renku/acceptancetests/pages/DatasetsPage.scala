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
import org.openqa.selenium.{WebDriver, WebElement}
import org.scalatestplus.selenium.WebBrowser.{cssSelector, find, findAll}

object DatasetsPage
    extends RenkuPage(
      path = s"/datasets",
      title = "Renku"
    )
    with TopBar {

  def searchBox(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#searchQuery")) getOrElse fail("Datasets -> search query field cannot be found")
  }

  def searchButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("#searchButton")) getOrElse fail("Datasets -> search button cannot be found")
  }

  def searchResultLinks(implicit webDriver: WebDriver): List[WebElement] = eventually {
    findAll(cssSelector(".rk-search-result-card > a > div > div.title")).toList
  }

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(
    searchResultLinks.headOption getOrElse searchBox
  )
}
