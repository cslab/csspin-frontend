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

"""
Spin plugin wrapper for the tool cypress.

Allows running cypress tests in a spin environment. Therefore this plugin will
start the services necessary for the testing.
"""

import os

try:
    from csspin import config, die, option, setenv, sh, task
except ImportError:
    from spin import config, die, option, setenv, sh, task

defaults = config(
    version="13.6.3",
    base_url="http://localhost:8080",
    browser="chrome",
    requires=config(
        spin=[
            "csspin_ce.ce_services",
            "csspin_ce.mkinstance",
            "csspin_frontend.node",
            "csspin_python.python",
        ],
        npm=["cypress@{cypress.version}"],
    ),
)


def _run_cypress(  # pylint: disable=keyword-arg-before-vararg
    cfg,
    instance,
    run=True,
    *args,
):
    from ce_services import RequireAllServices
    from csspin_ce.ce_services import extract_service_config

    subcommand = "run" if run else "open"
    inst = os.path.abspath(instance or cfg.mkinstance.base.instance_location)
    if not os.path.isdir(inst):
        die(f"Cannot find the CE instance '{inst}'.")
    setenv(CADDOK_BASE=inst)
    setenv(CYPRESS_adminpwd="{mkinstance.base.instance_admpwd}")

    with RequireAllServices(cfg_overwrite=extract_service_config(cfg)):
        if subcommand == "run":
            sh(
                "npx",
                "cypress",
                subcommand,
                "--project",
                "{spin.project_root}",
                "--config",
                f"baseUrl={cfg.cypress.base_url}",
                "--browser",
                f"{cfg.cypress.browser}",
                *args,
            )
        else:
            sh(
                "npx",
                "cypress",
                subcommand,
                "--project",
                f"{cfg.spin.project_root}",
                "--config",
                f"baseUrl={cfg.cypress.base_url}",
                *args,
            )


@task(when="cept")
def cypress(
    cfg,
    instance: option(
        "-i",  # noqa: F821
        "--instance",  # noqa: F821
        help="Directory of the CONTACT Elements instance.",  # noqa: F722
    ),
    coverage: option(  # pylint: disable=unused-argument
        "-c",  # noqa: F821
        "--coverage",  # noqa: F821
        is_flag=True,
        help="Run the tests while collecting coverage.",  # noqa: F722
    ),  # Needed for cept workflow
    args,
):
    """Run the 'cypress run' command."""
    _run_cypress(cfg, instance, True, *args)


@task("cypress:open")
def cypress_open(
    cfg,
    instance: option(
        "-i",  # noqa: F821
        "--instance",  # noqa: F821
        help="Directory of the CONTACT Elements instance.",  # noqa: F722
    ),
    coverage: option(  # pylint: disable=unused-argument
        "-c",  # noqa: F821
        "--coverage",  # noqa: F821
        is_flag=True,
        help="Run the tests while collecting coverage.",  # noqa: F722
    ),  # Needed for cept workflow
    args,
):
    """Run the 'cypress open' command."""
    _run_cypress(cfg, instance, False, *args)
