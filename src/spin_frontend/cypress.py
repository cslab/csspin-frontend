# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2024 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
Spin plugin wrapper for the tool cypress.

Allows running cypress tests in a spin environment. Therefore this plugin will
start the services necessary for the testing.
"""

import os

from spin import config, die, option, setenv, sh, task

defaults = config(
    version="13.6.3",
    base_url="http://localhost:8080",
    browser="chrome",
    requires=config(
        spin=[
            "spin_ce.ce_services",
            "spin_ce.mkinstance",
            "spin_frontend.node",
            "spin_python.python",
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
    from spin_ce.ce_services import extract_service_config

    subcommand = "run" if run else "open"
    inst = os.path.abspath(instance or cfg.mkinstance.dbms)
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
    instance: option("-i", "--instance"),  # noqa: F821
    coverage: option(  # pylint: disable=unused-argument
        "-c", "--coverage", is_flag=True  # noqa: F821
    ),  # Needed for cept workflow
    args,
):
    """Run the 'cypress run' command."""
    _run_cypress(cfg, instance, True, *args)


@task("cypress:open")
def cypress_open(
    cfg,
    instance: option("-i", "--instance"),  # noqa: F821
    coverage: option(  # pylint: disable=unused-argument
        "-c", "--coverage", is_flag=True  # noqa: F821
    ),  # Needed for cept workflow
    args,
):
    """Run the 'cypress open' command."""
    _run_cypress(cfg, instance, False, *args)
