# -*- coding: utf-8 -*-

import pytest
from .patch_serializer import patch_serializer, ExtraQueryError
from collections import defaultdict
from .utils import build_report_table


class ExplicitQueriesPlugin(object):
    def __init__(self, plugin_manager):
        self.extra_queries = defaultdict(list)

    def add_extra_query(self, extra_query: ExtraQueryError):
        key = f"{extra_query.serializer_name}_{extra_query.field}_{extra_query.function_name}"

        self.extra_queries[key].append(extra_query)

    # TODO: haha, revise, move out of plugin
    def get_most_consuming_serializers(self):
        """Returns the most consuming queries made by each serializers"""

        def get_most_consuming_query(serializer_errors):
            return sorted(
                serializer_errors, key=lambda e: len(e.queries), reverse=True
            )[0]

        return sorted(
            [
                get_most_consuming_query(serializer_errors)
                for serializer_errors in self.extra_queries.values()
            ],
            key=lambda error: error.serializer_name,
        )

    def pytest_terminal_summary(self, terminalreporter):

        if not self.extra_queries:
            return

        terminalreporter.section("YEEEY")
        report_table = build_report_table(self.get_most_consuming_serializers())

        for extra_query in report_table:
            terminalreporter.write(extra_query)
            terminalreporter.write("\n")


# TODO: fix make this work
# https://docs.pytest.org/en/latest/writing_plugins.html#setuptools-entry-points
# @pytest.mark.tryfirst
# def pytest_load_initial_conftests(early_config, parser, args):
#     print(f"\n\n\n\n\n\n\n\n\n\n\n\n\n\nAAAAAAAAAAAA\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
#     # if early_config.known_args_namespace.cov_source:
#     plugin = ExplicitQueriesPlugin(early_config.pluginmanager)
#     early_config.pluginmanager.register(plugin, "_explicit")


@pytest.hookspec(historic=True)
def pytest_configure(config):
    plugin = ExplicitQueriesPlugin(config.pluginmanager)

    config.pluginmanager.register(plugin, "_explicit")
    patch_serializer(plugin)


# TODO: fix make this work
def pytest_addoption(parser):
    group = parser.getgroup("django-explicit-queries")
    group.addoption(
        "--name",
        action="store",
        dest="name",
        default="World",
        help='Default "name" for hello().',
    )
