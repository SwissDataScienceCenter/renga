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

import ch.renku.acceptancetests.model.projects.ProjectDetails
import ch.renku.acceptancetests.pages._
import ch.renku.acceptancetests.tooling.AcceptanceSpec

trait Fork {
  self: AcceptanceSpec with RemoveProject =>

  def `fork project`(projectDetails: ProjectDetails): Unit = {
    val projectPage = ProjectPage()(projectDetails, userCredentials)
    go to projectPage

    When("user clicks on the fork button")
    click on projectPage.forkButton

    val forkedProjectDetails = ProjectDetails.generate()

    And(s"fills in the title (${forkedProjectDetails.title}) and submits")
    projectPage.ForkDialog.submitFormWith(forkedProjectDetails)

    Then("the project gets forked and the project page gets displayed")
    val forkedProjectPage = ProjectPage()(forkedProjectDetails, userCredentials)
    verify browserAt forkedProjectPage

    `remove project in GitLab`(forkedProjectDetails)
    `verify project is removed`(forkedProjectDetails)
  }
}
