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

import ch.renku.acceptancetests.model.datasets.DatasetName
import ch.renku.acceptancetests.pages.JupyterLabPage
import ch.renku.acceptancetests.tooling.{AcceptanceSpec, KnowledgeGraphApi}

import scala.concurrent.duration._

trait JupyterNotebook extends Datasets with Project with KnowledgeGraphApi {
  self: AcceptanceSpec =>

  def `create a dataset`(jupyterLabPage: JupyterLabPage, datasetName: DatasetName): Unit = {
    import jupyterLabPage.terminal

    terminal %> s"renku dataset create '$datasetName'" sleep (2 seconds)
    And("pushes it")
    terminal %> "git push" sleep (30 seconds)
  }

  def `verify user can work with Jupyter notebook`: Unit = {
    val jupyterLabPage = `launch a session`

    When("the user clicks on the Terminal icon")
    click on jupyterLabPage.terminalIcon sleep (2 seconds)
    val datasetName = DatasetName.generate
    And("the user creates a dataset")
    `create a dataset`(jupyterLabPage, datasetName)

    `stop session`

    When("all the events are processed by the knowledge-graph")
    `wait for KG to process events`(projectDetails.asProjectIdentifier)

    Then("the user can see the created dataset")
    `verify dataset was created`(datasetName)
  }
}
