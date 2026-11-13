# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2024 CONTACT Software GmbH
# https://www.contact-software.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module implementing the jest plugin for csspin."""

import os

from csspin import Verbosity, config, die, interpolate1, mkdir, option, setenv, sh, task
from path import Path

_SONAR_REPORTER_PACKAGE = "@casualbot/jest-sonar-reporter"

defaults = config(
    coverage=False,
    coverage_opts=[
        "--coverage",
        f"--coverageDirectory={{spin.project_root}}{os.path.sep}jest_coverage",
    ],
    opts=[
        "--ci",
        "--passWithNoTests",
        "--noStackTrace",
    ],
    report_opts=["--reporters=default", f"--reporters={_SONAR_REPORTER_PACKAGE}"],
    source="{spin.project_root}/cs",
    requires=config(
        spin=[
            "csspin_python.python",
            "csspin_frontend.node",
            "csspin_ce.mkinstance",
        ],
        python=["cs.web"],
    ),
)


def _install_sonar_reporter(spin_dir: Path) -> Path:
    """Install _SONAR_REPORTER_PACKAGE into its own directory, independent
    of cs.webmake's node_modules, and return the path to its package
    directory.
    """
    reporter_dir = spin_dir / "jest-sonar-reporter"
    mkdir(reporter_dir)
    package_json = reporter_dir / "package.json"
    if not package_json.exists():
        package_json.write_text("{}\n")
    # Without this, yarn may treat an enclosing directory as this one's
    # workspace root and refuse to add here as a standalone project.
    yarn_lock = reporter_dir / "yarn.lock"
    if not yarn_lock.exists():
        yarn_lock.write_text("")
    # Yarn defaults to Plug'n'Play (no node_modules at all) without this.
    yarnrc = reporter_dir / ".yarnrc.yml"
    if not yarnrc.exists():
        yarnrc.write_text("nodeLinker: node-modules\n")

    sh("yarn", "add", _SONAR_REPORTER_PACKAGE, cwd=reporter_dir)

    return reporter_dir / "node_modules" / _SONAR_REPORTER_PACKAGE


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
    instance: option(
        "-i",  # noqa: F821
        "--instance",  # noqa: F821
        default=None,
        help="Directory of the CONTACT Elements instance.",  # noqa: F722
    ),
    coverage: option(
        "-c",  # noqa: F821
        "--coverage",  # noqa: F821
        is_flag=True,
        help="Run the tests while collecting coverage.",  # noqa: F722
    ),
    with_test_report: option(
        "--with-test-report",  # noqa: F722
        is_flag=True,
        help="Create a test execution report.",  # noqa: F722
    ),
    debug: option(
        "--debug", is_flag=True, help="Start debug server."  # noqa: F722,F821
    ),
    args,
):
    """Run jest tests against a CE instance."""
    if not (
        instance := Path(instance or cfg.mkinstance.base.instance_location).absolute()
    ).is_dir():
        die(f"Cannot find CE instance '{instance}'.")

    opts = cfg.jest.opts
    if cfg.verbosity > Verbosity.NORMAL:
        opts.append("--verbose")
    if coverage or cfg.jest.coverage:
        opts.extend(cfg.jest.coverage_opts)
    if debug:
        opts.append("--debug")
    if with_test_report and cfg.jest.report_opts:
        reporter_package = _install_sonar_reporter(cfg.spin.spin_dir)

        setenv(
            JEST_SONAR_OUTPUT_DIR=cfg.spin.project_root,
            JEST_SONAR_OUTPUT_NAME="jest-sonar.xml",
        )

        # report_opts is interpolated before tasks run, so the resolved reporter
        # path can only be substituted here.
        opts.extend(
            opt.replace(_SONAR_REPORTER_PACKAGE, str(reporter_package))
            for opt in cfg.jest.report_opts
        )

    setenv(CADDOK_BASE=instance)
    sh("webmake", "-D", instance, "run-tests", cfg.spin.project_name, *opts, *args)
    setenv(CADDOK_BASE=None)
