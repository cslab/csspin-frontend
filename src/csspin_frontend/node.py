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
interpreter. If a version is specified, the plugin will install the specified
version of Node.js using nodeenv. The plugin also installs npm and other
required npm packages.
"""

import sys
from os import symlink
from textwrap import dedent

try:
    from csspin import (
        Path,
        config,
        copy,
        die,
        exists,
        get_requires,
        interpolate1,
        memoizer,
        rmtree,
        setenv,
        sh,
        writetext,
    )
    from csspin.tree import ConfigTree
except ImportError:
    from spin import (
        Path,
        config,
        copy,
        die,
        exists,
        get_requires,
        interpolate1,
        memoizer,
        rmtree,
        setenv,
        sh,
        writetext,
    )
    from spin.tree import ConfigTree

defaults = config(
    version=None,
    use=None,
    mirror=None,
    ignore_ssl_certs=False,
    requires=config(
        spin=["csspin_python.python"],
        python=["nodeenv"],
        npm=["sass", "yarn"],
    ),
)


def configure(cfg: ConfigTree) -> None:
    """Configure the node plugin"""
    if interpolate1("{node.use}") != "None":
        cfg.node.requires.python = []

    if cfg.node.version is None and not cfg.node.use:
        die(
            "Spin's Node.js plugin does not set a default version.\n"
            "Please choose a version in spinfile.yaml by setting"
            " node.version"
        )
    if cfg.node.version == "system":
        die("Can't use node.version=system. Try node.use instead.")

    if cfg.node.use and not exists(cfg.node.use):
        import shutil

        if not (interpreter := shutil.which(cfg.node.use)):
            die(f"Could not finde Node interpreter '{cfg.node.use}'")
        cfg.node.use = Path(interpreter)


def provision(cfg: ConfigTree, *args: str) -> None:
    """Provision the node plugin"""
    npm = cfg.python.scriptdir / "npm"
    if sys.platform == "win32":
        npm += ".cmd"
        npm_prefix_path = cfg.python.venv / "Scripts"
        node_path = npm_prefix_path / "node_modules"
    else:
        npm_prefix_path = cfg.python.venv
        node_path = npm_prefix_path / "lib" / "node_modules"

    with memoizer("{python.venv}/nodeversions.memo") as m:
        if cfg.node.use:
            if not m.check(cfg.node.use):
                setenv(
                    NODE_PATH=node_path,
                    NPM_CONFIG_PREFIX=npm_prefix_path,
                )
                node_dir = cfg.node.use.dirname()
                if sys.platform == "win32":
                    copy(cfg.node.use, cfg.python.scriptdir)
                    create_npm_cmd(cfg, node_dir)
                else:
                    copy(cfg.node.use, cfg.python.scriptdir)
                    symlink(node_dir / "npm", cfg.python.scriptdir / "npm")
                m.add(cfg.node.use)

        elif cfg.node.version and (
            cfg.node.version in ("latest", "lts") or not m.check(cfg.node.version)
        ):
            setenv(
                NODE_PATH=node_path,
                NPM_CONFIG_PREFIX=npm_prefix_path,
            )
            cmd = [
                cfg.python.python,
                "-mnodeenv",
                "--python-virtualenv",
                f"--node={cfg.node.version}",
            ]
            if cfg.node.mirror:
                cmd.append(f"--mirror={cfg.node.mirror}")
            if cfg.node.ignore_ssl_certs:
                cmd.append("--ignore-ssl-certs")
            sh(*cmd, *args)
            m.add(cfg.node.version)

        for plugin in cfg.spin.topo_plugins:
            plugin_module = cfg.loaded[plugin]
            for req in get_requires(plugin_module.defaults, "npm"):
                if not m.check(req):
                    sh(npm, "install", "-g", req)
                    m.add(req)


def create_npm_cmd(cfg: ConfigTree, node_dir: Path) -> None:
    """Writes an npm.cmd into the venv's Scripts directory which can be used to
    execute npm.cmd from another directory.
    """
    cmd = dedent(
        rf"""
        @echo off
        setlocal

        set NPM_EXEC={node_dir}\npm.cmd
        if not exist "%NPM_EXEC%" (
            echo Error: npm not found at %NPM_EXEC%
            exit /b 1
        )
        "%NPM_EXEC%" %*
        endlocal
    """
    )
    writetext(cfg.python.scriptdir / "npm.cmd", cmd)


def cleanup(cfg: ConfigTree) -> None:  # pylint: disable=W0613
    """Remove directories and files generated by the frontend plugin."""
    rmtree("node_modules")
