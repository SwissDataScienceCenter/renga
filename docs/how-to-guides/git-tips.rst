.. _git_tips:

Git cheat sheet for Renku
=========================

Renku is based on ``git`` so here is a cheat sheet to make your life a bit
easier.

**To undo what you just did:**

.. code-block:: console

    git reset --hard HEAD~1

(this means, move my git history back by one commit from where I currently stand)

**To go back to a sane state:** First find the "sane state" with ``git log``, e.g.

.. code-block:: console

    $ git log
    commit 7df2389f3e7df6c013467b399e4de23b0f2f4b78
    Author: Rok Roskar <roskarr@ethz.ch>
    Date:   Thu Oct 4 01:04:04 2018 +0200

        renku run python src/plot_data.py data/preprocessed/zhbikes.parquet

    commit e6590bd40bdda10339417b992d1869523915b767
    Author: Rok Roskar <roskarr@ethz.ch>
    Date:   Thu Oct 4 01:03:14 2018 +0200

        renku run python src/clean_data.py data/zhvelo ...

    commit b3ce8ac5b9d239fd710b3be2ae2afad1f7a4509d
    Author: Rok Roskar <roskarr@ethz.ch>
    Date:   Thu Oct 4 00:56:36 2018 +0200

        renku dataset add zhvelo --relative-to data/zhvelo ...
        git+ssh://renkulab.io/team-renku/zurich-bikes-data.git

    commit f346c1f36f211840b22a63e7fc2c9bfb52616212
    Author: Rok Roskar <roskarr@ethz.ch>
    Date:   Wed Oct 3 22:26:38 2018 +0200

        renku dataset create zhvelo


Now lets say you decide your data imports and everything that followed was
wrong and you want to go back to ``renku dataset create zhvelo``, i.e.
commit ``f346c1f36f211840b22a63e7fc2c9bfb52616212``, you would do:

.. code-block:: console

    git reset --hard f346c1f36f211840b22a63e7fc2c9bfb52616212

Easy!
