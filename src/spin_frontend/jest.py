# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2024 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Module implementing the jest plugin for cs.spin."""

from path import Path
from spin import Verbosity, config, die, interpolate1, option, setenv, sh, task

defaults = config(
    coverage=False,
    coverage_opts=["--coverage"],
    opts=[
        "--ci",
        "--passWithNoTests",
        "--noStackTrace",
    ],
    report_opts=[
        "--reporters=default",
        "--reporters=jest-junit",
    ],
    source="{spin.project_root}/cs",
    requires=config(
        spin=[
            "spin_python.python",
            "spin_frontend.node",
            "spin_ce.mkinstance",
        ],
        python=["cs.web"],
    ),
)


def configure(cfg):
    """Configure the jest plugin"""
    for path in Path(interpolate1(cfg.jest.source)).walk():
        if any(conf in path for conf in ("jest.config.js", "jest.config.json")):
            break
    else:
        die("No jest.conf.json or jest.conf.js found for this project!")


@task(when="test")
def jest(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    cfg,
    instance: option("-i", "--instance", default=None),  # noqa: F821
    coverage: option("-c", "--coverage", is_flag=True),  # noqa: F821
    with_test_report: option("--with-test-report", is_flag=True),  # noqa: F821,F722
    debug: option("--debug", is_flag=True),  # noqa: F821
    args,
):
    """Run jest tests against a CE instance."""
    if not (instance := Path(instance or cfg.mkinstance.dbms).absolute()).is_dir():
        die(f"Cannot find CE instance '{instance}'.")

    opts = cfg.jest.opts
    if cfg.verbosity > Verbosity.NORMAL:
        opts.append("--verbose")
    if coverage or cfg.jest.coverage:
        opts.extend(cfg.jest.coverage_opts)
    if debug:
        opts.append("--debug")
    if with_test_report and cfg.jest.report_opts:
        opts.extend(cfg.jest.report_opts)

    setenv(CADDOK_BASE=instance)
    sh("webmake", "-D", instance, "run-tests", cfg.spin.project_name, *opts, *args)
    setenv(CADDOK_BASE=None)
