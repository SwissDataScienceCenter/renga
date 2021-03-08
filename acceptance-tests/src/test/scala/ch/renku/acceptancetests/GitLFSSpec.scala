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

package ch.renku.acceptancetests

import ch.renku.acceptancetests.model.datasets.{DatasetDir, DatasetName, DatasetURL}
import ch.renku.acceptancetests.tooling.AcceptanceSpec
import ch.renku.acceptancetests.workflows._

import scala.language.postfixOps

class GitLFSSpec
    extends AcceptanceSpec
    with Collaboration
    with Environments
    with Login
    with Project
    with JupyterNotebook
    with RemoveProject
    with Datasets {

  scenario("User can start a notebook with auto-fetch LFS") {

    `log in to Renku`

    `create, continue or open a project`

    val importDatasetURL    = DatasetURL("10.7910/DVN/WTZS4K") // TODO parametrize?
    val importedDatasetName = DatasetName("2019-01 US Flights")
    And("an imported dataset for this project")
    val importedDatasetPage = `import a dataset`(importDatasetURL, importedDatasetName)
    // val test = importedDatasetPage.path.value
    // val datasetPage = DatasetPage(importedDatasetName)
    // val datasetLink = projectPage.Datasets.DatasetsList.link(to = datasetPage)(_: WebDriver)

    val importedDatasetDirectory =
      DatasetDir("201901_us_flights_10/2019-01-flights.csv.zip") // TODO get path from datasets link element
    `verify auto LFS dataset on Jupyter Notebook`(importedDatasetDirectory)

    `log out of Renku`
  }
}
