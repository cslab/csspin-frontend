# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2020 CONTACT Software GmbH
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

"""This module implements the node plugin for csspin.

This plugin allows you to use Node.js in your spin environment. It can be
configured to use a specific version of Node.js or to use the system's Node.js
interpreter. If a version is specified, the plugin will install download the the
specified version of Node.js as an artifact and will store it in spin.data. The
plugin also installs npm and other required npm packages.
"""

from __future__ import annotations

import json
import shutil
import sys
import tarfile
import typing
import zipfile
from functools import cache
from subprocess import PIPE  # nosec
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import urlopen

if typing.TYPE_CHECKING:
    from typing import Any

try:
    from csspin import (
        Path,
        config,
        copy,
        die,
        download,
        exists,
        get_requires,
        interpolate1,
        memoizer,
        mkdir,
        mv,
        setenv,
        sh,
        warn,
    )
    from csspin.tree import ConfigTree
except ImportError:
    from spin import (
        Path,
        config,
        copy,
        die,
        download,
        exists,
        get_requires,
        interpolate1,
        memoizer,
        mkdir,
        mv,
        setenv,
        sh,
    )
    from spin.tree import ConfigTree


defaults = config(
    install_dir="{spin.data}/nodejs/",
    version=None,
    use=None,
    mirror="https://nodejs.org/dist/",
    requires=config(
        spin=["csspin_python.python"],
        npm=[
            "sass",
            "yarn",
        ],
    ),
)


def configure(cfg: ConfigTree) -> None:
    """Configure the node plugin"""
    if cfg.node.version is None and not cfg.node.use:
        die(
            "Spin's Node.js plugin does not set a default version.\n"
            "Please choose a version in spinfile.yaml by setting"
            " node.version"
        )

    if cfg.node.use:
        if cfg.node.version:
            warn(
                "node.version will be ignored, using '{node.use}' from node.use instead."
            )
        if not exists(cfg.node.use):
            if not (interpreter := shutil.which(cfg.node.use)):
                die(f"Could not finde Node interpreter '{cfg.node.use}'")
            cfg.node.use = Path(interpreter)

    if cfg.node.mirror and not cfg.node.mirror.endswith("/"):
        cfg.node.mirror = f"{cfg.node.mirror}/"


def provision(cfg: ConfigTree) -> None:
    """Provision the node plugin"""
    cmd_postfix = ".cmd" if sys.platform == "win32" else ""

    node = cfg.node.use or _download_node(cfg)
    node_in_venv = cfg.python.scriptdir / f"node{cfg.platform.exe}"

    npm = cfg.python.scriptdir / f"npm{cmd_postfix}"
    outside_npm = node.dirname() / f"npm{cmd_postfix}"

    if not outside_npm.exists():
        die(f"npm does not exist at {outside_npm}")

    node_changed = False
    if sys.platform == "win32":
        if not node_in_venv.exists():
            copy(node, node_in_venv)
            node_changed = True
        node_path = cfg.python.scriptdir / "node_modules"
        npm_config_prefix = cfg.python.scriptdir
    else:
        if (
            not node_in_venv.exists()
            or not node_in_venv.islink()
            or node_in_venv.readlink() != node
        ):
            node_in_venv.remove_p()
            node_in_venv.symlink_to(node)
            node_changed = True
        node_path = cfg.python.venv / "lib/node_modules"
        npm_config_prefix = cfg.python.venv

    setenv(
        NODE_PATH=node_path,
        NPM_CONFIG_PREFIX=npm_config_prefix,
        npm_config_prefix=npm_config_prefix,
    )

    if not npm.exists() or node_changed:
        npm_req = f"npm@{_get_npm_version(cfg, node)}"
        _install_requirements([npm_req], npm=outside_npm, memo=False)

    requirements = []
    for plugin in cfg.spin.topo_plugins:
        plugin_module = cfg.loaded[plugin]
        requirements += get_requires(plugin_module.defaults, "npm")
    _install_requirements(requirements)


@cache
def _fetch_node_dist_index(base_url) -> Any:
    """
    Download "nodejs.org/dist/index.json" which contains information about
    available nodejs versions and the matching npm versions.
    """
    url = urljoin(base_url, "index.json")
    try:
        with urlopen(url) as response:  # nosec: blacklist
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError):
        die(
            f"Could not lookup node/npm versions on {url}. "
            "Please check '{{{{node.mirror}}}}' or your internet connection."
        )
    except json.JSONDecodeError:
        die(
            f"Could not lookup node/npm versions on {url}. The response seems to be malformed."
        )
    return data


def _determine_exact_node_version(  # pylint: disable=inconsistent-return-statements
    cfg: ConfigTree,
) -> str:
    """
    Get the version string of nodejs that we can find with the given value of cfg.node.version.

    The function will return:
        - The latest lts version if cfg.node.version is "lts"
        - The latest major/major.minor version, if only the major/major.minor
          version are provided, with or without a leading "v"
        - The version with a leading "v" if it was missing
    """
    node_index_data = _fetch_node_dist_index(cfg.node.mirror)
    cfg.node.version = interpolate1(cfg.node.version)  # Cast into str
    if cfg.node.version.lower() == "lts":
        # node_index_data is sorted, so let's just return the first LTS version
        for node_version_data in node_index_data:
            if node_version_data["lts"]:
                return node_version_data["version"]
    else:
        if not cfg.node.version.startswith("v"):
            cfg.node.version = f"v{cfg.node.version}"
        for node_version_data in node_index_data:
            current_version = node_version_data["version"]
            if current_version.startswith(cfg.node.version):
                return current_version
    die(f"Could not determine a node version for '{cfg.node.version}'")


def _get_npm_version(  # pylint: disable=inconsistent-return-statements
    cfg: ConfigTree, node: Path
) -> str:
    """Get the recommended npm version for the given node interpreter"""
    versions = {
        entry["version"]: entry["npm"]
        for entry in _fetch_node_dist_index(cfg.node.mirror)
        if "version" in entry and "npm" in entry
    }
    proc = sh(node, "--version", stdout=PIPE, encoding="utf-8", silent=True)
    try:
        return versions[proc.stdout.strip()]
    except KeyError:
        die(f"Could not determine the npm version for {node}")


def _install_requirements(reqs: list[str], npm: Path | None = None, memo=True) -> None:
    """
    Install npm requirements into the environment and memoize them. If
    installing npm memoizing should not be done, as otherwise the npm version
    may not fit for the node version.
    """
    _npm = npm or "npm"
    if not memo:
        sh(_npm, "install", "-g", *reqs)
    else:
        with memoizer("{python.venv}/node_modules.memo") as m:
            to_install = [req for req in reqs if not m.check(req)]
            if not to_install:
                return
            sh(_npm, "install", "-g", *to_install)
            for req in reqs:
                m.add(req)


def _download_node(cfg: ConfigTree) -> Path:
    """
    Download and unzip the configured node archive into {spin.data}/nodejs.
    Returns the path to the node executable.
    """
    node_install_base = interpolate1(Path("{spin.data}/nodejs/"))
    exact_node_version = _determine_exact_node_version(cfg)
    node_dir = node_install_base / exact_node_version
    if sys.platform == "win32":
        node = node_dir / "node.exe"
    else:
        node = node_dir / "bin" / "node"
    if node.exists():
        return node

    if sys.platform == "win32":
        archive_ext = ".zip"
        archive_base_name = f"node-{exact_node_version}-win-x64"
    else:
        archive_ext = ".tar.xz"
        archive_base_name = f"node-{exact_node_version}-linux-x64"
    archive = f"{archive_base_name}{archive_ext}"
    url = urljoin(cfg.node.mirror, f"{exact_node_version}/{archive}")

    with TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / archive
        try:
            download(url, archive_path)
        except (HTTPError, URLError):
            die(f"Error while downloading {url}")
        if tarfile.is_tarfile(archive_path):
            extractor = tarfile.open
            mode = "r:xz"
        elif zipfile.is_zipfile(archive_path):
            extractor = zipfile.ZipFile
            mode = "r"
        else:
            raise KeyError("Unsupported archive type...")

        with extractor(archive_path, mode=mode) as arc:
            arc.extractall(
                path=tmp_dir,
            )  # nosec: tarfile_unsafe_members
        mkdir(node_install_base)
        mv(Path(tmp_dir) / archive_base_name, node_dir)
    return node
