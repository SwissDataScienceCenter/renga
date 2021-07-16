.. _pull-requests:

Contributing to Renku repositories
==================================

All our code base is available in the repositories in
`our GitHub organization <https://github.com/SwissDataScienceCenter>`_.
Apart from a few exceptions, we generally require any change to the ``master``
branch to go through a review process.

Merge changes
-------------

This is the standard flow:

- Create a new branch, either on the target repository or on your fork,
  and open a pull request to merge the branch to `master`. If that addresses
  an issue, it's good practice to prefix the name with the issue number.

  .. note::

    For a PR fixing issue 1234, you can use a branch name like
    `1234-fix-project-creation`.
  
- Verify that the tests pass and fix them if required. Remember to add new
  tests and adapt the existing ones whenever the changes to the code base
  justify it.
- Ask for a review from one of the developers responsible for the repository.
  If possible, add to the reviewers also the person who opened the issue.
  Mind that some repositories automatically require review from specific
  groups of people when opening the PR.
- Once approved, you can merge the PR. Try to stick with the following rules:

  - Follow the
    `Conventional Commits specifications <https://github.com/SwissDataScienceCenter>`_
    when writing a commit message.
  - Always mention the reference issue in the commit body (use `fix #1234`
    or `re #1234`), unless the PR doesn't explicitly fix any issue.
  - Include the PR number in the commit main message.

    .. note::

      For the PR 1235 fixing the issue 1234, you can write

      .. code-block::

        feat: add new parameter for initialization (#1235)
        fix #1234


  - Squash the PR commits when merging to ``master`` *without creating an
    extra merge commit*. If you prefer to keep more than one commit, you
    can rebase on your branch before merging.

Special cases
^^^^^^^^^^^^^

When dealing with one of our most important repositories (
`renku <https://github.com/SwissDataScienceCenter/renku>`_
`renku-gateway <https://github.com/SwissDataScienceCenter/renku-gateway>`_
`renku-graph <https://github.com/SwissDataScienceCenter/renku-graph>`_
`renku-notebooks <https://github.com/SwissDataScienceCenter/renku-notebooks>`_
`renku-python <https://github.com/SwissDataScienceCenter/renku-python>`_
`renku-ui <https://github.com/SwissDataScienceCenter/renku-ui>`_),
it's important that you run the
`acceptance tests <https://github.com/SwissDataScienceCenter/renku/tree/master/acceptance-tests>`_
and create a testing environment.

We use
`dedicated GitHub actions <https://github.com/SwissDataScienceCenter/renku/tree/master/actions>`_
to automatize this process. This still requires something on your side since
we don't create such an environment for every PR.

The easiest way to deploy a test environment (including the changes from your
PR) is to include the string-command ``/deploy`` anywhere in your PR
description. That will trigger our CI.

You can specify a few extra bits after the command, like a
tag/branch for other components (E.G. ``/deploy renku-ui=0.11.9``) or the
``#notest`` string that prevents the acceptance tests from running when
it's not needed.

.. note::

  The acceptance tests take a long time to run. You can skip them whenever
  the change doesn't affect the code (E.G. readme file, comments, etc.).

Please refer to the
`"check PR description" <https://github.com/SwissDataScienceCenter/renku/tree/master/actions/check-pr-description>`_
action for further information about the commands supported by the
``/deploy`` keyword.
