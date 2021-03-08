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

import ch.renku.acceptancetests.model.projects.{ProjectDetails, ProjectIdentifier}
import ch.renku.acceptancetests.pages._
import ch.renku.acceptancetests.tooling.{AcceptanceSpec, AnonEnvConfig}
import org.openqa.selenium.WebDriver

import scala.concurrent.duration._

trait Environments {
  self: AcceptanceSpec =>

  def `launch an environment`(implicit projectDetails: ProjectDetails, projectPage: ProjectPage): JupyterLabPage = {
    When("user clicks on the Environments tab")
    click on projectPage.Environments.tab
    docsScreenshots.takeScreenshot()

    `click new & wait for image to build`
    docsScreenshots.takeScreenshot()

    `start environment & wait util it's not ready`
    docsScreenshots.takeScreenshot()

    projectPage.Environments.Running.connectToJupyterLab

    Then("a JupyterLab page is opened on a new tab")
    val jupyterLabPage = JupyterLabPage()
    verify browserSwitchedTo jupyterLabPage sleep (5 seconds)
    jupyterLabPage
  }

  def `stop environment`(implicit projectDetails: ProjectDetails): Unit =
    stopEnvironmentOnProjectPage(ProjectPage())

  def `stop environment`(projectId: ProjectIdentifier): Unit =
    stopEnvironmentOnProjectPage(ProjectPage(projectId))

  private def stopEnvironmentOnProjectPage(projectPage: ProjectPage): Unit = {
    When("the user switches back to the Renku tab")
    verify browserSwitchedTo projectPage
    And("the Environments tab")
    click on projectPage.Environments.tab
    And("they turn off the interactive session they started before")
    click on projectPage.Environments.Running.connectDotButton
    click on projectPage.Environments.Running.stopButton sleep (10 seconds)
    Then("the session gets stopped and they can see the New Session link")
    verify userCanSee projectPage.Environments.newLink
  }

  def `launch an environment with Auto Fetch`(implicit
      projectDetails: ProjectDetails,
      projectPage:    ProjectPage
  ): JupyterLabPage = {
    When("user clicks on the Environments tab")
    click on projectPage.Environments.tab

    `click new & wait for image to build`

    `turn Auto Fetch On`

    `start environment & wait util it's not ready`

    projectPage.Environments.Running.connectToJupyterLab

    Then("a JupyterLab page is opened on a new tab")
    val jupyterLabPage = JupyterLabPage()
    verify browserSwitchedTo jupyterLabPage sleep (5 seconds)
    jupyterLabPage
  }

  def `launch anonymous environment`(anonEnvConfig: AnonEnvConfig): Option[JupyterLabPage] = {
    val projectId   = anonEnvConfig.projectId
    val projectPage = ProjectPage(projectId)
    go to projectPage
    When("user is logged out")
    And(s"goes to $projectId")
    And("clicks on the Environments tab to launch an anonymous notebook")
    click on projectPage.Environments.tab
    if (anonEnvConfig.isAvailable) {
      And("anonymous environments are supported")
      Some(`anonymous environment supported`(projectPage, projectId))
    } else {
      And("anonymous environments are not supported")
      `anonymous environment unsupported`(projectPage)
      None
    }
  }

  def `launch unprivileged environment`(implicit anonEnvConfig: AnonEnvConfig): JupyterLabPage = {
    val projectId = anonEnvConfig.projectId
    implicit val projectPage: ProjectPage = ProjectPage(projectId)
    go to projectPage
    When(s"user goes to $projectId")
    And("clicks on the Environments tab to launch an unprivileged notebook")
    click on projectPage.Environments.tab

    `click new & wait for image to build`
    `start environment & wait util it's not ready`

    projectPage.Environments.Running.connectToJupyterLab

    Then("a JupyterLab page is opened on a new tab")
    val jupyterLabPage = JupyterLabPage(projectId)
    // TODO This does not work for some reason
    // verify browserSwitchedTo jupyterLabPage sleep (5 seconds)
    jupyterLabPage
  }

  private def `anonymous environment unsupported`(projectPage: ProjectPage): Option[JupyterLabPage] = {
    Then("they should see a message")
    projectPage.Environments.anonymousUnsupported
    None
  }

  private def `anonymous environment supported`(pp: ProjectPage, projectId: ProjectIdentifier): JupyterLabPage = {
    implicit val projectPage: ProjectPage = pp
    sleep(5 seconds)
    `click new & wait for image to build`
    `start environment & wait util it's not ready`

    projectPage.Environments.Running.connectToAnonymousJupyterLab

    Then("a JupyterLab page is opened on a new tab")
    val jupyterLabPage = JupyterLabPage(projectId)
    // TODO This does not work for some reason
    // verify browserSwitchedTo jupyterLabPage sleep (5 seconds)
    jupyterLabPage
  }

  private def `click new & wait for image to build`(implicit projectPage: ProjectPage): Unit = {
    And("then they click on the New link")
    click on projectPage.Environments.newLink sleep (2 seconds)
    And("once the image is built")
    projectPage.Environments.verifyImageReady sleep (2 seconds)
  }

  private def `turn Auto Fetch On`(implicit projectPage: ProjectPage): Unit = {
    And("then they turn on the Auto-fetch option")
    click on projectPage.Environments.autoFetch
  }

  private def `start environment & wait util it's not ready`(implicit projectPage: ProjectPage): Unit =
    projectPage.Environments.maybeStartEnvironment match {
      case None =>
        projectPage.Environments.connectToJupyterLabLink.isDisplayed shouldBe true
      case Some(startEnvButton) =>
        And("the user clicks on the Start Environment button")
        click on startEnvButton sleep (5 seconds)

        `try few times before giving up` { (_: WebDriver) =>
          Then("they should be redirected to the Environments -> Running tab")
          verify userCanSee projectPage.Environments.Running.title
        }

        `try few times before giving up` { (_: WebDriver) =>
          When("the environment is ready")
          projectPage.Environments.Running.verifyEnvironmentReady
        }

        And("the user clicks on the Connect button in the table")
        // Sleep a little while after clicking to give the server a chance to come up
        click on projectPage.Environments.Running.title sleep (30 seconds)
    }
}
