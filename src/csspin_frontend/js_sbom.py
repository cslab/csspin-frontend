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

"""Module implementing the js_sbom plugin for csspin-frontend"""

import sysconfig
from pathlib import Path as PathlibPath

from csspin import config, copy, exists, info, rmtree, setenv, sh, task
from csspin.tree import ConfigTree
from path import Path

defaults = config(requires=config(spin=["csspin_python.python"]))


@task("js-sbom", when="sbom:build")
def sbom(cfg: ConfigTree) -> None:
    """Build the SBOMs for JavaScript applications of the current project"""
    js_build_dir = cfg.spin.project_root / "build"
    if not exists(js_build_dir):
        setenv(PIP_INDEX_URL=cfg.python.index_url)
        sh("python", "setup.py", "build_js")
        setenv(PIP_INDEX_URL=None)
    else:
        info(f"JS bundles already built {js_build_dir}, skipping build step.")

    _collect_js_sboms(cfg.spin.project_root)


def _collect_js_sboms(project_root: Path) -> None:
    """
    Collect the built bom.json files and place them top level named by namespace
    """
    build_lib = PathlibPath(project_root) / "build" / "lib"

    for sbom_path in build_lib.glob("**/bom/bom.json"):
        parts = sbom_path.relative_to(build_lib).parts
        name_parts = [p for p in parts[:-3] if p != "js"]
        platform_tag = sysconfig.get_platform().replace("-", "_")
        dest_name = "-".join(name_parts) + f".{platform_tag}.js_sbom.cdx.json"

        copy(sbom_path, project_root / dest_name)
        info(f"Collected SBOM: {dest_name}")


def cleanup(cfg: ConfigTree) -> None:
    """Cleanup generated files"""
    rmtree(cfg.spin.project_root / "build")
    for cdx_file in cfg.spin.project_root.glob("*.js_sbom.cdx.json"):
        rmtree(cdx_file)
