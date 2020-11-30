#!/usr/bin/env python3
#
# Usage: ./deploy_dev_renku -h
#
# Note: you can use the following environment variables to set defaults:
#
# RENKU_VALUES_FILE
# RENKU_RELEASE
# RENKU_NAMESPACE
#

import argparse
import os
import pprint
import re
import tempfile

from pathlib import Path
from subprocess import check_call

import yaml

components = [
    "renku-core",
    "renku-gateway",
    "renku-graph",
    "renku-notebooks",
    "renku-ui",
]


class RenkuRequirement(object):
    """Class for handling custom renku requirements."""

    def __init__(self, component, version, tempdir):
        self.component = component
        self.tempdir = tempdir

        self.version_ = version
        self.is_git_ref = False
        if version.startswith("@"):
            # this is a git ref
            self.is_git_ref = True

    @property
    def ref(self):
        if self.is_git_ref:
            return self.version_.strip("@")
        return None

    @property
    def version(self):
        if self.is_git_ref:
            self.clone()
            self.chartpress(skip_build=True)
            with open(
                self.repo_dir / "helm-chart" / self.component / "Chart.yaml"
            ) as f:
                chart = yaml.load(f)
            return chart.get("version")
        return self.version_

    @property
    def helm_repo(self):
        if self.ref:
            return f"file://{self.tempdir}/{self.repo}/helm-chart/{self.component}"
        return "https://swissdatasciencecenter.github.io/helm-charts/"

    # handle the special case of renku-python
    @property
    def repo(self):
        if self.component == "renku-core":
            return "renku-python"
        return self.component

    @property
    def repo_url(self):
        if self.component == "renku-core":
            return f"https://github.com/SwissDataScienceCenter/renku-python.git"
        return f"https://github.com/SwissDataScienceCenter/{self.component}.git"

    @property
    def repo_dir(self):
        return Path(f"{self.tempdir}/{self.repo}")

    def clone(self):
        """Clone repo and reset to ref."""
        if not self.repo_dir.exists():
            check_call(
                [
                    "git",
                    "clone",
                    self.repo_url,
                    self.repo_dir,
                ]
            )
        check_call(["git", "checkout", self.ref], cwd=self.repo_dir)

    def chartpress(self, skip_build=False):
        """Run chartpress."""
        check_call(
            ["helm", "dep", "update", f"helm-chart/{self.component}"], cwd=self.repo_dir
        )
        cmd = ["chartpress", "--push"]
        if skip_build:
            cmd.append("--skip-build")
        check_call(cmd, cwd=self.repo_dir)

    def setup(self):
        """Checkout the repo and run chartpress."""
        self.clone()
        self.chartpress(skip_build=True)


def configure_requirements(tempdir, reqs, component_versions):
    """
    Reads versions from environment variables and renders the requirements.yaml file.

    If any of the requested versions reference a git ref, the chart is rendered and
    images built and pushed to dockerhub.
    """
    for component, version in component_versions.items():
        if version:
            # form and setup the requirement
            req = RenkuRequirement(component.replace("_", "-"), version, tempdir)
            if req.ref:
                req.setup()
                # replace the requirement
            for dep in reqs["dependencies"]:
                if dep["name"] == component.replace("_", "-"):
                    dep["version"] = req.version
                    dep["repository"] = req.helm_repo
                    continue
    return reqs


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    for component in components:
        parser.add_argument(f"--{component}", help=f"Version or ref for {component}")
    parser.add_argument("--renku", help="Main chart ref")
    parser.add_argument(
        "--values-file",
        help="Value file path",
        default=os.environ.get("RENKU_VALUES_FILE"),
    )
    parser.add_argument(
        "--namespace",
        help="Namespace for this release",
        default=os.environ.get("RENKU_NAMESPACE"),
    )
    parser.add_argument(
        "--release", help="Release name", default=os.environ.get("RENKU_RELEASE")
    )

    args = parser.parse_args()
    component_versions = {
        a: b for a, b in vars(args).items() if a.replace("_", "-") in components
    }

    tempdir_ = tempfile.TemporaryDirectory()
    tempdir = Path(tempdir_.name)

    renku_dir = tempdir / "renku"
    reqs_path = renku_dir / "charts/renku/requirements.yaml"

    ## 1. clone the renku repo
    check_call(
        [
            "git",
            "clone",
            "https://github.com/SwissDataScienceCenter/renku.git",
            renku_dir,
        ]
    )
    if args.renku:
        check_call(["git", "checkout", args.renku], cwd=renku_dir)

    with open(reqs_path) as f:
        reqs = yaml.load(f)

    ## 2. set the chosen versions in the requirements.yaml file
    reqs = configure_requirements(tempdir, reqs, component_versions)

    with open(reqs_path, "w") as f:
        yaml.dump(reqs, f)

    ## 3. run helm dep update renku
    check_call(["helm3", "dep", "update", "renku"], cwd=renku_dir / "charts")

    ## 4. deploy
    values_file = args.values_file
    release = args.release
    namespace = args.namespace

    print(f'*** Dependencies for release "{release}" under namespace "{namespace}" ***')
    pprint.pp(reqs)

    check_call(
        [
            "helm3",
            "upgrade",
            "--install",
            release,
            "./renku",
            "-f",
            values_file,
            "--namespace",
            namespace,
        ],
        cwd=renku_dir / "charts",
    )

    tempdir_.cleanup()
