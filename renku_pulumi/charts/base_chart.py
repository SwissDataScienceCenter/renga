from base64 import b64encode

import yaml
import pulumi
from pulumi_kubernetes.helm.v2 import Chart, ChartOpts, FetchOpts
from pulumi_random.random_password import RandomPassword
from pulumi_random.random_id import RandomId
from deepmerge import always_merger


class BaseChart(Chart):
    name = None
    chart_name = None
    default_values_template = {}
    release_name = None

    def __init__(self, config, global_config=None, dependencies=[]):
        self.global_config = global_config

        stack = pulumi.get_stack()

        if not self.chart_name:
            self.chart_name = self.name

        if not self.release_name:
            self.release_name = "{}-{}".format(stack, self.name)

        dependencies = [d for d in dependencies if d]

        self.dependencies = dependencies
        super().__init__(self.release_name, self.chart_opts, opts=self.opts)

    @property
    def chart_requirements(self):
        """Get chart requirements."""

        with open('chart_requirements.yaml', 'r') as f:
            chart_reqs = yaml.load(f, Loader=yaml.FullLoader)

        return chart_reqs.get(self.name, {})

    @property
    def chart_opts(self):
        """Get the Chart config."""
        return ChartOpts(
            chart=self.chart_name,
            version=self.chart_version,
            repo=self.chart_repo,
            fetch_opts=self.fetch_opts,
            values=self.values,
        )

    @property
    def fetch_opts(self):
        """Get chart fetch_opts."""
        repo = self.chart_requirements["repository"]
        if repo.startswith("http"):
            return FetchOpts(repo=repo)
        return None

    @property
    def chart_repo(self):
        """Get chart fetch_opts."""
        repo = self.chart_requirements["repository"]
        if repo.startswith("http"):
            return None

        return repo

    @property
    def chart_version(self):
        """Get the version of the chart to deploy."""
        return self.chart_requirements["version"]

    @property
    def opts(self):
        """Custom Chart options."""
        if self.dependencies:
            return pulumi.ResourceOptions(depends_on=self.dependencies)

        return None

    @property
    def default_values(self):
        """Get chart default values."""
        return self.default_values_template

    @property
    def pulumi_config(self):
        """Get the pulumi config for this chart object."""
        return pulumi.Config(self.name)

    @property
    def values(self):
        """Get chart values."""
        chart_config = self.pulumi_config
        values = chart_config.get_object("values") or {}

        values = always_merger.merge(self.default_values, values)

        values = self.values_post_process(values)

        values["global"] = self.global_config["global"]
        self.global_config[self.name] = values

        return values

    def values_post_process(self, values):
        """Postprocessing of values."""
        return values

    def base64encode(self, value):
        """Helper to b64 encode strings."""
        return b64encode(value.encode()).decode("ascii")

    def generate_random_password(self, name, length, configured_value=None):
        """Helper method to generated a random password."""
        if configured_value:
            return pulumi.Output.from_input(
                    configured_value
                ).apply(lambda r: self.base64encode(r))

        return RandomPassword(
                name,
                length=length,
                special=False,
                number=True,
                upper=False,
                lower=True,
            ).result.apply(lambda r: self.base64encode(r))

    def generate_random_id(self, name, length=8):
        """Helper method to generated a random id."""
        return RandomId(
                name, byte_length=length
            ).hex.apply(lambda r: self.base64encode(r))

    def delayed_chart_property(self, chart, selector, property_name):
        """Gets a delayed/future property of a resource in a ``Chart``."""
        def log_resources_on_exception(r):
            try:
                return next(s for k, s in r.items() if selector(k, s))
            except:
                with open("resource.log", "w") as f:
                    f.write(self.name + "\n")
                    f.write(chart.name + "\n")
                    f.write(property_name + "\n")
                    for k, s in r.items():
                        f.write(k + "\n")
                        f.write(repr(s) + "\n\n")
                raise

        return chart.resources.apply(log_resources_on_exception).metadata[property_name]
