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

"""Module implementing the jsconfig plugin for csspin

This plugin searches for JavaScript packages in order to create a jsconfig.json
file that can be interpreted by IDE's to enhance syntax highlighting,
quick-fixes, documentation previews, and more.
"""

import fnmatch
import json
import os
import re

from path import Path

try:
    from csspin import config, confirm, echo, exists, info, option, rmtree, task, warn
except ImportError:
    from spin import config, confirm, echo, exists, info, option, rmtree, task, warn

defaults = config(
    includes=["cs/**/*"],
    excludes=[
        "**/build",
        "**/node_modules",
    ],
    search_dirs=["{python.site_packages}"],
    base_url="{spin.project_root}",
    requires=config(spin=["csspin_python.python"]),
)


def finalize_provision(cfg):  # pylint: disable=unused-argument
    """Create a jsconfig.json file if not already present."""
    if not exists(cfg.spin.project_root / "jsconfig.json"):
        generate_jsconfig(cfg)
    else:
        info("jsconfig.json already exists, not generating new one.")


@task()
def jsconfig(
    cfg,
    skip_confirmation: option(
        "--yes",  # noqa: F821
        "-y",  # noqa: F821
        "skip_confirmation",  # noqa: F821
        is_flag=True,
        hidden=True,
    ),
):
    """Generate a jsconfig.json file"""
    if not (
        not exists("jsconfig.json")
        or skip_confirmation
        or confirm("You are about to override the jsconfig.json. Continue?")
    ):
        generate_jsconfig(cfg)


def generate_jsconfig(cfg):
    """Generates the jsconfig.json file"""

    paths_by_package_names = {}
    exclude_patterns = [
        re.compile(fnmatch.translate(pattern)) for pattern in cfg.jsconfig.excludes
    ]

    for dir_to_search in cfg.jsconfig.search_dirs:
        info(f"Searching for package.json files in {dir_to_search}")

        for dirpath, _, filenames in os.walk(dir_to_search):
            if any(pattern.search(dirpath) for pattern in exclude_patterns):
                continue

            dirpath = Path(dirpath)
            for filename in filenames:
                if filename != "package.json":
                    continue

                info(f"Found {filename} at {dirpath}")
                try:
                    # Get the package's name and use it as the key for the list
                    # of relative paths that lead to this package. We might have
                    # multiple paths in case the search_dirs contain multiple
                    # versions of the same cs package.
                    with open(
                        dirpath / filename,
                        "r",
                        encoding="utf-8",
                    ) as json_file:

                        if package_name := json.load(json_file).get("name"):
                            # Add package path to the list for the package name
                            paths_by_package_names.setdefault(package_name, []).append(
                                dirpath.relpath(cfg.spin.project_root)
                            )
                except (IOError, json.JSONDecodeError) as ex:
                    warn(f"Error when trying to handle {filename}: {str(ex)}")

    jsconfig_json = {
        "include": cfg.jsconfig.includes,
        "exclude": cfg.jsconfig.excludes,
        "compilerOptions": {"baseUrl": cfg.jsconfig.base_url, "paths": {}},
    }

    for package_name, paths in paths_by_package_names.items():
        jsconfig_json["compilerOptions"]["paths"][package_name] = [
            path.replace(os.sep, "/") for path in paths
        ]

    with open(
        target_jsconfig_path := cfg.spin.project_root / "jsconfig.json",
        "w",
        encoding="utf-8",
    ) as jsconfig_file:
        json.dump(jsconfig_json, jsconfig_file, indent=4, sort_keys=True)

    echo(
        f"jsconfig.json generated successfully: {target_jsconfig_path}!",
        "Some IDE's may require a restart to apply the config.",
    )


def cleanup(cfg):
    """Remove the jsconfig.json file"""
    rmtree(cfg.spin.project_root / "jsconfig.json")
