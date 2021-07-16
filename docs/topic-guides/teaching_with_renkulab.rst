.. _teaching_with_renkulab:

Teaching with Renkulab
======================

One of the bottlenecks in teaching analysis and programming skills is that often
a large portion of the session is spent installing software. A few reasons for this
are the following:

* the software dependencies themselves might take a long time to install
* bugs! students might have different operating systems than the instructors and
  the versions might not be the same or might not exist at all, in some cases

Renkulab bypasses the struggle by allowing instructors to create templates
as starting points for students to interact with the instructional material:

* the instructor creates a new project and writes the dependencies in one place
  (e.g. a ``Dockerfile`` and/or ``requirements.txt`` and/or ``install.R``)
* students "fork" (make a copy) of the project to use as a starting point
* students can launch sessions (e.g. JupyterLab and/or RStudio)
  where these dependencies are pre-installed.

From their copy of the starter project that the instructor creates, students can
then independently build on the project from inside the session
by adding and modifying code, extra software dependencies, etc., which they can
then save (by ``git commit`` & ``git push``) back to Renkulab.

FAQ
^^^

Privacy & Group Settings: If I create a project on the public instance of Renkulab, who will be able to access it?

Updates: If I make an update to the course material, how can I ensure that students will receive these updates?
