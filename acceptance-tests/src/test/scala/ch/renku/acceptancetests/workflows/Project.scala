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

import ch.renku.acceptancetests.model.projects.{ProjectDetails, Template, Visibility}
import ch.renku.acceptancetests.pages._
import ch.renku.acceptancetests.tooling.AcceptanceSpec
import org.scalatest.BeforeAndAfterAll

import java.lang.System.getProperty
import scala.concurrent.duration._

trait PrivateProject extends Project with BeforeAndAfterAll {
  self: AcceptanceSpec =>

  protected override lazy val projectVisibility: Visibility = Visibility.Private
  protected implicit override lazy val projectDetails: ProjectDetails =
    ProjectDetails.generate().copy(visibility = projectVisibility)
}

trait Project extends RemoveProject with BeforeAndAfterAll {
  self: AcceptanceSpec =>

  protected lazy val projectVisibility: Visibility = Visibility.Public

  protected implicit lazy val projectDetails: ProjectDetails =
    Option
      .when(docsScreenshots.captureScreenshots)(docsScreenshots.projectDetails)
      .orElse(maybeExtantProject)
      .getOrElse(ProjectDetails.generate())

  protected implicit lazy val projectPage: ProjectPage = ProjectPage.createFrom(projectDetails)

  def `create, continue or open a project`: Unit = maybeExtantProject match {
    case Some(_) => `open a project`
    case _       => `create or continue with a project`
  }

  private def `create or continue with a project`: Unit =
    if (`project exists in GitLab`(projectDetails.asProjectIdentifier)) `open a project`
    else `create a new project`

  private def `open a project`: Unit = {

    When("user click on the Projects in the Top Bar")
    click on projectPage.TopBar.projects sleep (2 seconds)

    And("they click on the 'Your Projects' tab")
    click on ProjectsPage.YourProjects.tab

    And("they enter project title in the search box")
    ProjectsPage.YourProjects.searchField.clear() sleep (1 second)
    ProjectsPage.YourProjects.searchField.enterValue(projectDetails.title)

    And("they click the Search button")
    click on ProjectsPage.YourProjects.searchButton sleep (1 second)

    Then(s"the '${projectDetails.title}' project should be listed")
    val projectLink = ProjectsPage.YourProjects.linkTo(projectDetails)

    When("they click on the link")
    click on projectLink sleep (1 second)

    `try few times before giving up` { _ =>
      Then(s"they should see the '${projectDetails.title}' project page")
      verify browserAt projectPage
    }
  }

  private def `create a new project`: Unit = {
    if (WelcomePage.TopBar.mainNavToggler.isDisplayed())
      click on WelcomePage.TopBar.mainNavToggler

    When("user clicks on the 'New Project' menu item")
    click on WelcomePage.TopBar.plusDropdown
    click on WelcomePage.TopBar.projectOption sleep (5 seconds)

    `try few times before giving up` { _ =>
      Then("the New Project page gets displayed")
      verify browserAt NewProjectPage
    }

    `try few times before giving up` { _ =>
      When("user fills in and submits the new project details form")
      NewProjectPage submitFormWith projectDetails
    }

    pause asLongAsBrowserAt NewProjectPage
    Then(s"the project '${projectDetails.title}' gets created and the Project page gets displayed")

    val projectPage = ProjectPage createFrom projectDetails
    verify browserAt projectPage

    When("the user navigates to the Overview -> Description tab")
    click on projectPage.Overview.tab
    click on projectPage.Overview.overviewGeneralButton
    Then("they should see project's README.md content")
    verify that projectPage.Overview.Description.title is "README.md"

    When("the user navigates to the Files tab")
    click on projectPage.Files.tab
    And("they click on the README.md file in the File View")
    click on (projectPage.Files.FileView file "README.md") sleep (2 seconds)
    Then("they should see the file header")
    verify that projectPage.Files.Info.heading contains "README.md"
    And("the commit hash")
    verify that projectPage.Files.Info.commit matches "^Commit: [0-9a-f]{8}$"
    And("creator name and timestamp")
    verify that projectPage.Files.Info.creatorAndTime contains userCredentials.fullName
    And("the readme header which is the project title")
    verify that projectPage.Files.Info.title is projectDetails.readmeTitle
    And("the readme content")
    verify that projectPage.Files.Info.content contains "This is a Renku project"
  }

  private lazy val maybeExtantProject: Option[ProjectDetails] =
    (Option(getProperty("extant")) orElse sys.env.get("RENKU_TEST_EXTANT_PROJECT"))
      .map(_.trim)
      .map { readMeTitle =>
        ProjectDetails(readMeTitle,
                       projectVisibility,
                       description = "unused",
                       template = Template("Not used"),
                       readmeTitle = readMeTitle
        )
      }

  protected override def afterAll(): Unit = {
    maybeExtantProject match {
      case Some(_) => ()
      case _       => `remove project in GitLab`(projectDetails.asProjectIdentifier)
    }

    super.afterAll()
  }
}
