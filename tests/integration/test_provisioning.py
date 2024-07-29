# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2024 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Module implementing the integration tests for spin_frontend"""

import functools
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

NODE_EXISTS = shutil.which("node")


def run_command_in_env(cmd, spin_cmd):
    """Helper function to run a subprocess in a provisioned spin environment."""
    command = spin_cmd.copy()
    command.extend(cmd)
    print(subprocess.list2cmdline(command))
    return subprocess.check_output(command, encoding="utf-8").strip()


@functools.cache
def provision_env(spinfile, tmp_path):
    """
    Helper function to provision a spin environment based on the spinfile provided by
    spinfile.

    Returns a tuple (cache, cmd) where `cache` is the location of the
    provisioned environments cache-dir and `cmd` is a commandline as a list to
    build commands to run subprocesses inside the provisioned env.
    """
    if spinfile == "node_use.yaml" and not shutil.which("node"):
        pytest.skip("node not available")

    spinfile_path = os.path.join("tests", "integration", "yamls", spinfile)
    cache = tmp_path / ".cache"
    cache.mkdir(parents=True, exist_ok=True)

    base_cmd = [
        "spin",
        "-q",
        "-p",
        f"spin.cache={cache}",
        "-C",
        "tests/integration",
        "--env",
        str(tmp_path),
        "-f",
        spinfile_path,
    ]
    cmd = base_cmd + ["--provision"]
    print(subprocess.list2cmdline(cmd))
    try:
        subprocess.check_output(cmd, encoding="utf-8", stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        print(ex.stdout)
    return (tmp_path, base_cmd)


TESTCASES = (
    pytest.param("node_version.yaml", "node", "18.17.0", id="node_version.yaml:node"),
    pytest.param("node_version.yaml", "sass", "1.77.5", id="node_version.yaml:sass"),
    pytest.param("node_version.yaml", "yarn", "1.22.21", id="node_version.yaml:yarn"),
    pytest.param(
        "node_use.yaml",
        "node",
        (
            None
            if not NODE_EXISTS
            else subprocess.check_output(
                ["node", "--version"],
                encoding="utf-8",
            ).strip()
        ),
        id="node_use.yaml:node",
        marks=pytest.mark.skipif(not NODE_EXISTS, reason="node not installed."),
    ),
    pytest.param("node_use.yaml", "sass", "1.77.5", id="node_use.yaml:sass"),
    pytest.param("node_use.yaml", "yarn", "1.22.21", id="node_use.yaml:yarn"),
    pytest.param("cypress.yaml", "cypress", "10.3.0", id="cypress.yaml:cypress"),
)


@pytest.mark.integration()
@pytest.mark.parametrize("spinfile, tool, _version", TESTCASES)
def test_tool_path(spinfile, tool, _version, tmp_dir_per_spinfile):
    """
    Check whether the expected tools with the correct version is available in
    the provisioned env.
    """
    tmp_path, env_cmd = provision_env(spinfile, tmp_dir_per_spinfile)

    if sys.platform == "win32":
        cmd = [
            "run",
            "powershell",
            "-C",
            f"(get-command {tool}).path",
        ]
    else:
        cmd = ["run", "which", tool]
    tool_path = Path(run_command_in_env(cmd, env_cmd))
    assert tmp_path in tool_path.parents


@pytest.mark.integration()
@pytest.mark.parametrize("spinfile, tool, version", TESTCASES)
def test_tool_version(spinfile, tool, version, tmp_dir_per_spinfile):
    """
    Check whether the expected tools with the correct version is available in
    the provisioned env.
    """
    _, env_cmd = provision_env(spinfile, tmp_dir_per_spinfile)

    assert version in run_command_in_env(["run", tool, "--version"], env_cmd)
