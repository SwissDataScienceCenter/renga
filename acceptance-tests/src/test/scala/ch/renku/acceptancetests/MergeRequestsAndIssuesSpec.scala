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

import ch.renku.acceptancetests.tooling.{AcceptanceSpec, KnowledgeGraphApi}
import ch.renku.acceptancetests.workflows._

import scala.concurrent.duration._

class MergeRequestsAndIssuesSpec
    extends AcceptanceSpec
    with Collaboration
    with Login
    with Project
    with KnowledgeGraphApi {

  Scenario("User can create and view issues") {

    `log in to Renku`

    `create, continue or open a project`

    `verify there are no issues`

    val issueTitle = "test issue"
    val issueDesc  = "test description"
    `create a new issue`(issueTitle, issueDesc)

    `view the issue`(issueTitle)

    `log out of Renku`
  }

  Scenario("User can create and view merge requests") {

    `log in to Renku`

    `create, continue or open a project`

    `verify there are no merge requests`

    val branchName = "test-branch"
    `add change to the project`(branchName)

    `create a new merge request`

    `view the merge request`(branchName)

    `log out of Renku`
  }

  private def `add change to the project`(branchName: String): Unit = {
    docsScreenshots.disable()
    val jupyterLabPage = `launch an environment`
    docsScreenshots.enable()

    When("the user clicks on the Terminal icon")
    click on jupyterLabPage.terminalIcon sleep (2 seconds)

    `create a branch in JupyterLab`(jupyterLabPage, branchName)

    `wait for KG to process events`(projectDetails.asProjectIdentifier)

    `stop environment`
  }
}
