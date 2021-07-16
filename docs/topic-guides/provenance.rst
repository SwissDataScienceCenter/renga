.. _provenance:

Provenance of results
=====================

One of the most important ideas behind Renku is the concept of capturing the
**provenance** of the analysis process. Lets assume we are working with ``input
data``, ``code``, and ``results``:

.. graphviz::
    :align: center

    graph foo {
        rankdir="LR"
        nodesep=0.01
        node [fontname="Raleway"]
        _results [color="white", label="", image="../_static/icons/scatter_plot.svg"]
        results [color="white"]
        _code [color="white", label="", image="../_static/icons/electronics.svg"]
        code [color="white"]
        data [color="white", label="", image="../_static/icons/data_sheet.svg"]
        "input data" [color="white"]


        _results--results [color="white"]
        _code--code [color="white"]
        data--"input data" [color="white"]
    }

If you write a piece of code that takes some input data, processes it and
writes some output to disk, the **provenance graph** would look something like
this:

.. graphviz::
    :align: center

    digraph foo {
        rankdir="LR"
        edge [fontname="Raleway"]
        data [color="white", label="", image="../_static/icons/data_sheet.svg"]
        code [color="white", label="", image="../_static/icons/electronics.svg"]
        results [color="white", label="", image="../_static/icons/scatter_plot.svg"]
        data->code [label="used by"]
        code->results [label="generated"]
    }


Naturally, a ``result`` may also be used as ``input data`` to a subsequent step:

.. graphviz::
    :align: center

    digraph foo {
        edge [fontname="Raleway"]
        rankdir="LR"
        data [color="white", label="", image="../_static/icons/data_sheet.svg"]
        data2 [color="white", label="", image="../_static/icons/data_sheet2.svg"]
        code [color="white", label="", image="../_static/icons/electronics.svg"]
        code2 [color="white", label="", image="../_static/icons/electronics2.svg"]
        results [color="white", label="", image="../_static/icons/scatter_plot.svg"]
        results2 [color="white", label="", image="../_static/icons/scatter_plot2.svg"]
        data->code
        code->results
        results->code2
        data2->code2
        code2->results2
    }

In a real analysis, such a graph may become very complex. Without a detailed
record of the connections between the different data, code and result blocks,
it may be impossible to efficiently regenerate parts of the chain. Keeping
track of the provenance allows us to easily recreate the final result if the
original raw data changes, for example, or to examine what happens when we
change our preprocessing pipeline. Recording provenance is also critical for
enabling data and code audits, should they be required.

We hope that using Renku will encourage people to share their data, results,
and analysis codes. By capturing the provenance not only within, but also *across*
projects we ensure that if you use someone else's results you can always
track exactly where they came from. Conversely, you can also see how someone
is using your shared data or code in their analysis. Renku will allow you to
explore these connections in detail.


Recording Provenance in Renku
-----------------------------

Keeping track of provenance manually is a tedious process. In Renku we try to
automate this as much as possible by providing a simple command-line interface which,
when used correctly, should take care of provenance recording for you. The basic
idea is as follows: anything you run in the terminal to produce a result simply
needs to have `renku run` pre-pended to it and you are done. This will work best
if these assumptions are met:

* The code which is run to compute a result can be started from the terminal.
* The data inputs are specified as arguments to the command.
* The data outputs are within the project directory tree and not outside (i.e. cannot be in a parent directory)

An example execution would look something like:

.. code-block:: console

    $ renku run python run_analysis.py -i inputs -o outputs

Wrapping the execution of ``python run_analysis.py`` with ``renku run`` had
the following consequences:

1. The command was executed.
2. If it completed successfully, a `Common Workflow Language (CWL) <https://www.commonwl.org/>`_ tool specification was created, linking this command-line invocation to the inputs and outputs.
3. Everything was committed to the git repository.

CWL is an emerging standard for describing scientific workflows. By using this
standard, we hope to ensure the longevity of results as well as the interoperability
of provenance information recorded in Renku with other tools and platforms.


Applying the Provenance
-----------------------

In Renku, we want to provide tools that not only record the provenance but also
give you easy access to its benefits. Once the provenance is recorded, there are
several ways in which it can become immediately beneficial. The most common
usage is to **update** results when any of the input data or code
dependencies change. By knowing exactly which results depend on a particular
input, we can make sure to recompute only the necessary steps and not the
entire pipeline, potentially avoiding expensive calculations in complex
settings. For understanding the basic functionality, head to
`renkulab.io <https://renkulab.io>`_ and follow :ref:`first_steps`. See also
the Renkulab :ref:`knowledge graph<knowledge-graph>` documentation.
