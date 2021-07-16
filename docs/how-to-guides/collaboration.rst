.. _collaborating:

Collaborating on Renku
======================

Beyond building and maintaining your own data science workflows, there are many
ways to use Renku to share your project with collaborators.

Finding & accessing public projects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To find and access projects on the Renku platform that you might want to
interact with, you can click the **Projects** link in the menu bar followed by
the **Search** tab. Without entering any search terms, you will see a list of
all projects that you have access to. You can click on a project name to be
taken to the project's landing page.

By default, the files in projects created by other people are "read only" to you.
This means you can see an overview, create and read issues, and browse the filesystem
in both text and :ref:`provenance` modes. The project's **Environments** tab
will inform you that you do not have permissions to launch a notebook or make
modifications to the code or datasets.

If you would like to interact with the notebooks (run, edit, upload data, continue
your own analyses, etc.), you can `fork the project <forks_for_collaboration_>`_,
which creates your own copy of the current state of the repo.

If you have questions, notes, or discussion topics that you would communicate to
the project's owner(s), you can make `issues <make_issues_>`_

If you are part of the team and want to work on this project, you can ask the
project creator to `add you as a developer <added_to_project_>`_ or maintainer
of the project through GitLab.

.. _forks_for_collaboration:

Fork a project and take it in your own direction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Forking someone else's project on Renku is just like forking any version-controlled
project. The Renku platform provides you a fork button on the project's home page
that creates a fork of the project (with the same name) under your own namespace,
where you have permissions to launch notebooks and make settings modifications.

One reason you might want to fork someone's project is to use it as a template for
your own analysis.

.. _make_issues:

Add collaborators to the conversation through Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Renku, issues are media-rich discussions you can use to help keep track of
your work and to collaborate with others. To find out more about them and walk
through sample usage, see :ref:`sharing_is_caring`.

.. _added_to_project:

Add or be added as a developer on a project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To allow someone to make changes to your project, you can use the GitLab
interface to add them in ``Settings > Members``, with at either Developer or
Maintainer privileges.

Adding them here will make this project appear in their **Your Projects** list
on the Renku platform, where the **Environments** tab for the project will allow
them to launch a session to work on the project as usual.

.. warning::

  Note that with multi-person projects it's best for each person to make their
  changes in separate branches that you can later merge. For more information on
  how to branch and merge effectively, consult the git documentation.
