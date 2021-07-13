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

import ch.renku.acceptancetests.pages._
import ch.renku.acceptancetests.tooling.AcceptanceSpec

import scala.concurrent.duration._

trait Collaboration {
  self: AcceptanceSpec with Project =>

  def `navigate to the merge requests tab`: Unit = {
    When("the user navigates to the Collaboration tab")
    click on projectPage.Collaboration.tab sleep (1 second)
    And("they navigate to the Merge Requests sub tab")
    click on projectPage.Collaboration.MergeRequests.tab sleep (1 second)
  }

  def `verify that the GitLab MR iFrame is visible`: Unit = {
    Then("they should see the GitLab MR page in an iFrame")
    verify userCanSee projectPage.Collaboration.MergeRequests.collaborationIframe
  }

  def `verify that the GitLab MR page link is visible`: Unit = {
    Then("they should see a link to the GitLab MR page")
    verify userCanSee projectPage.Collaboration.MergeRequests.gitLabMrLink
  }

  def `navigate to the issues tab`: Unit = {
    When("the user navigates to the Collaboration tab")
    click on projectPage.Collaboration.tab sleep (1 second)
    And("they navigate to the Issues sub tab")
    click on projectPage.Collaboration.Issues.tab sleep (1 second)
  }

  def `verify that the GitLab issues iFrame is visible`: Unit = {
    Then("they should see the GitLab issues page in an iFrame")
    verify userCanSee projectPage.Collaboration.Issues.collaborationIframe
  }

  def `verify that the GitLab issues page link is visible`: Unit = {
    Then("they should see a link to the GitLab issues page")
    verify userCanSee projectPage.Collaboration.Issues.gitLabIssuesLink
  }

  def `create a branch in JupyterLab`(jupyterLabPage: JupyterLabPage, branchName: String): Unit = {
    import jupyterLabPage.terminal
    And("Creates a test branch")
    terminal %> "git checkout -b test-branch" sleep (10 seconds)
    And("Adds some Python packages to the requirements.txt")
    terminal %> "echo pandas==1.3.0 >> requirements.txt" sleep (1 second)
    terminal %> "echo seaborn==0.11.1 >> requirements.txt" sleep (1 second)
    And("Pushes changes to branch")
    terminal %> "git add ." sleep (2 seconds)
    terminal %> "git push --set-upstream origin test-branch" sleep (3 seconds)
    And("Checks out master again")
    terminal %> "git checkout master" sleep (4 seconds)
  }
}
