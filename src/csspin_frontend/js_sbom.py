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

import json
import sysconfig
from pathlib import Path as PathlibPath
from urllib.parse import quote, urlencode

from csspin import config, die, exists, info, rmtree, setenv, sh, task
from csspin.tree import ConfigTree
from csspin_python.python_sbom import _repository_base_url
from path import Path

defaults = config(
    repository_url="{python.index_url}",
    requires=config(spin=["csspin_python.python"]),
)


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

    _collect_js_sboms(cfg.spin.project_root, cfg.js_sbom.repository_url)


def _collect_js_sboms(project_root: Path, repository_url: str) -> None:
    """
    Collect the built bom.json files, fix up the primary component's purl,
    and place them top level named by namespace.
    """
    build_lib = PathlibPath(project_root) / "build" / "lib"

    for sbom_path in build_lib.glob("**/bom/bom.json"):
        parts = sbom_path.relative_to(build_lib).parts
        name_parts = [p for p in parts[:-3] if p != "js"]
        platform_tag = sysconfig.get_platform().replace("-", "_")
        dest_name = "-".join(name_parts) + f".{platform_tag}.js_sbom.cdx.json"

        with open(sbom_path, encoding="utf-8") as f:
            sbom_json = json.load(f)
        _fix_primary_component_purl(sbom_json, repository_url)

        with open(project_root / dest_name, "w", encoding="utf-8") as f:
            json.dump(sbom_json, f, indent=2, sort_keys=True)
        info(f"Collected SBOM: {dest_name}")


def cleanup(cfg: ConfigTree) -> None:
    """Cleanup generated files"""
    rmtree(cfg.spin.project_root / "build")
    for cdx_file in cfg.spin.project_root.glob("*.js_sbom.cdx.json"):
        rmtree(cdx_file)


# ---- Internals ---------------------------------------------------------------


def _build_js_purl(name: str, version: str, repository_url: str) -> str:
    """Build the npm Package URL.

    Setting the repository_url explicitly ensures to distinguish between npm
    packages published to npmjs.org and others. A scoped package name
    (``@scope/name``) is split into the purl's namespace and name segments,
    per the ``npm`` purl type definition.
    """
    scope, _, package_name = name.rpartition("/")
    namespace = quote(scope, safe=":") + "/" if scope else ""
    qualifiers = urlencode(
        sorted({"repository_url": _repository_base_url(repository_url)}.items()),
        safe=":",
    )
    pkgname = quote(package_name, safe=":")
    version = quote(version, safe=":")
    return f"pkg:npm/{namespace}{pkgname}@{version}?{qualifiers}"


def _fix_primary_component_purl(sbom_json: dict, repository_url: str) -> None:
    """
    Override the primary component's purl with one carrying repository_url.
    """
    info("Fixing primary component purl to include repository_url qualifier")
    component = sbom_json.get("metadata", {}).get("component")
    if not component or "name" not in component or "version" not in component:
        die("Primary component is missing name or version in SBOM metadata")

    old_ref = component.get("bom-ref") or component.get("purl")
    new_purl = _build_js_purl(component["name"], component["version"], repository_url)
    component["purl"] = new_purl
    component["bom-ref"] = new_purl

    for dependency in sbom_json.get("dependencies", []):
        if dependency.get("ref") == old_ref:
            dependency["ref"] = new_purl
