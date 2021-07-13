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

import ch.renku.acceptancetests.model.datasets.DatasetName
import org.openqa.selenium.interactions.Actions
import org.openqa.selenium.{WebDriver, WebElement}
import org.scalactic.source
import org.scalatest.enablers.Retrying
import org.scalatestplus.selenium.WebBrowser
import org.scalatestplus.selenium.WebBrowser.{cssSelector, find, findAll}

import scala.concurrent.duration._

object DatasetPage {
  def apply(datasetName: DatasetName)(implicit projectPage: ProjectPage) = new DatasetPage(datasetName, projectPage)
}

class DatasetPage(datasetName: DatasetName, projectPage: ProjectPage)
    extends RenkuPage(
      path = s"${projectPage.path}/datasets/${datasetName.asPath}",
      title = "Renku"
    )
    with TopBar {

  override def pageReadyElement(implicit webDriver: WebDriver): Option[WebElement] = Some(datasetTitle)

  def datasetTitle(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector(".col-md-8 > h3")) getOrElse fail("Dataset -> Dataset title not found")
  }

  def datasetNotInKgWarning(implicit webDriver: WebDriver): List[WebBrowser.Element] = eventually {
    findAll(cssSelector("#notInKGWarning")) toList
  }

  def datasetFiles(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector(".pl-3 > .order-third > a")) getOrElse fail("Dataset -> Dataset file not found")
  }

  def modifyButton(implicit webDriver: WebDriver): WebElement = eventually {
    find(cssSelector("a[href='modify']")) getOrElse fail("Dataset -> Modify button not found")
  }

  object ProjectsList {
    def link(to: ProjectPage)(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector(s"td a[href='${to.path}' i]"))
        .getOrElse(fail(s"Project '${to.path}' not found"))
    }(waitUpTo(20 seconds), implicitly[Retrying[WebBrowser.Element]], implicitly[source.Position])
  }

  object ModificationForm {

    def formTitle(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("h3.uk-heading-divider")) getOrElse fail("Form title not found")
    }

    def datasetTitleField(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("input[name='title']")) getOrElse fail("Dataset title field not found")
    }

    def datasetNameField(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("input[name='name']")) getOrElse fail("Dataset name field not found")
    }

    def datasetDescriptionField(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("div[role='textbox']")) getOrElse fail("Dataset description field not found")
    }

    def clickOnDatasetSubmitButton(implicit webDriver: WebDriver): Unit = eventually {
      val submitDatasetBtn =
        find(cssSelector("button[type='submit']")) getOrElse fail(
          "Dataset form submit button not found"
        )

      new Actions(webDriver)
        .moveToElement(submitDatasetBtn)
        .click()
        .build()
        .perform();
    }

    def fileUploadField(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("input[name='fileUrl']")) getOrElse fail("Dataset file upload field not found")
    }

    def fileUploadButton(implicit webDriver: WebDriver): WebElement = eventually {
      find(cssSelector("button[id='addFileButton']")) getOrElse fail("Dataset file upload button not found")
    }
  }
}
