#!/usr/bin/env python3
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2026 CONTACT Software GmbH
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
This script starts all services using ce_services and then starts cypress for
running e2e tests.

The script is intended to be run by the csspin_frontend.cypress plugin with the
interpreter from the provisioned environment, since otherwise the imports of
ce_services will not work. It should not be run directly.
"""

import argparse
import json
from subprocess import check_call  # nosec: blacklist

from ce_services import RequireAllServices


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("subcommand", choices=["run", "open"])
    parser.add_argument("--cfg", help="The config for ce_services to use.")
    parser.add_argument("--project_root", help="The root directory of the project.")
    parser.add_argument("--base_url", help="The URL cypress connects to.")
    parser.add_argument("--browser", help="The browser to use in 'run' mode.")
    parser.add_argument("args", nargs="*")
    parsed_args = parser.parse_args()
    return (
        parsed_args.subcommand,
        parsed_args.cfg,
        parsed_args.project_root,
        parsed_args.base_url,
        parsed_args.browser,
        parsed_args.args,
    )


def main():
    """Use cypress for e2e testing."""
    subcommand, cfg, project_root, url, browser, args = _cli()
    with open(cfg, "r", encoding="utf-8") as fd:
        cfg = json.load(fd)
    cmd = [
        "npx",
        "cypress",
        subcommand,
        "--project",
        project_root,
        "--config",
        f"baseUrl={url}",
    ]
    if subcommand == "run":
        cmd.extend(["--browser", browser])
    if args:
        subcommand.extend(*args)

    with RequireAllServices(cfg_overwrite=cfg):
        check_call(cmd)  # nosec: subprocess_without_shell_equals_true


if __name__ == "__main__":
    main()
