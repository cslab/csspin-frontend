# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2024 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Module implementing the integration tests for csspin_frontend"""

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

NODE_EXISTS = shutil.which("node")
NODE_DOES_NOT_EXIST_SKIP = pytest.mark.skipif(
    not NODE_EXISTS, reason="node not installed."
)
REDIS_EXISTS = shutil.which("redis-server")


def execute_spin(yaml, env, path="tests/integration/yamls", cmd=""):
    """Helper function to execute spin and return the output"""
    try:
        cmd = shlex.split(
            f"spin -q -p spin.data={env} -C {path} --env {env} -f {yaml} {cmd}",
            posix=sys.platform != "win32",
        )
        print(subprocess.list2cmdline(cmd))
        return subprocess.check_output(
            cmd,
            encoding="utf-8",
            stderr=subprocess.PIPE,
        ).strip()
    except subprocess.CalledProcessError as ex:
        print(ex.stdout)
        print(ex.stderr)
        raise


# Test cases for provisioning tools through plugins
TOOL_TESTCASES = (
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
        marks=NODE_DOES_NOT_EXIST_SKIP,
    ),
    pytest.param(
        "node_use.yaml",
        "sass",
        "1.77.5",
        id="node_use.yaml:sass",
        marks=NODE_DOES_NOT_EXIST_SKIP,
    ),
    pytest.param(
        "node_use.yaml",
        "yarn",
        "1.22.21",
        id="node_use.yaml:yarn",
        marks=NODE_DOES_NOT_EXIST_SKIP,
    ),
    pytest.param(
        "cypress.yaml",
        "cypress",
        "10.3.0",
        marks=pytest.mark.skipif(
            not REDIS_EXISTS,
            reason="redis not installed but required by spin_ce.ce_services dependency.",
        ),
        id="cypress.yaml:cypress",
    ),
)


@pytest.mark.integration()
@pytest.mark.parametrize("spinfile, tool, _version", TOOL_TESTCASES)
def test_tool_path(spinfile, tool, _version, tmp_dir_per_spinfile):
    """
    Check whether the expected tools with the correct version is available in
    the provisioned env.
    """
    execute_spin(yaml=spinfile, env=tmp_dir_per_spinfile, cmd="provision")

    if sys.platform == "win32":
        cmd = [
            "run",
            "powershell",
            "-C",
            f"(get-command {tool}).path",
        ]
    else:
        cmd = ["run", "which", tool]
    tool_path = Path(
        execute_spin(yaml=spinfile, env=tmp_dir_per_spinfile, cmd=" ".join(cmd))
    )
    assert tmp_dir_per_spinfile in tool_path.parents


@pytest.mark.integration()
@pytest.mark.parametrize("spinfile, tool, version", TOOL_TESTCASES)
def test_tool_version(spinfile, tool, version, tmp_dir_per_spinfile):
    """
    Check whether the expected tools with the correct version is available in
    the provisioned env.
    """
    execute_spin(yaml=spinfile, env=tmp_dir_per_spinfile, cmd="provision")
    assert version in execute_spin(
        yaml=spinfile, env=tmp_dir_per_spinfile, cmd=f"run {tool} --version"
    )


@pytest.mark.integration()
@pytest.mark.parametrize(
    "spinfile",
    [
        pytest.param("node_version.yaml", id="node_version.yaml"),
        pytest.param(
            "node_use.yaml", id="node_use.yaml", marks=NODE_DOES_NOT_EXIST_SKIP
        ),
    ],
)
def test_provision_a_second_time(spinfile, tmp_dir_per_spinfile):
    """
    Check whether the environment can be provisioned a second time without errors.
    """
    execute_spin(yaml=spinfile, env=tmp_dir_per_spinfile, cmd="provision")

    try:
        execute_spin(yaml=spinfile, env=tmp_dir_per_spinfile, cmd="provision")
    except subprocess.CalledProcessError as ex:
        pytest.fail(f"Second provisioning failed with returncode {ex.returncode}.")


@pytest.mark.integration()
@NODE_DOES_NOT_EXIST_SKIP
def test_jest_provision(tmp_path):
    """Provision the jest plugin"""
    yaml = "jest.yaml"
    execute_spin(yaml=yaml, env=tmp_path, cmd="provision")
    execute_spin(yaml=yaml, env=tmp_path, cmd="jest --help")


@pytest.mark.integration()
@NODE_DOES_NOT_EXIST_SKIP
def test_jsconfig_provision(tmp_path):
    """Provision the jsconfig plugin"""
    yaml = "jsconfig.yaml"
    # jsconfig.json is created in spin.project_root, so lets define it here in
    # order to delete the generated file at the end of the test.
    # The project_root can't be set to some temporary directory, because this
    # depends on the location of the spinfile passed.
    project_root = Path("tests/integration/yamls")

    try:
        execute_spin(yaml=yaml, env=tmp_path, path=project_root, cmd="provision")
        assert (project_root / "jsconfig.json").exists()

        execute_spin(yaml=yaml, env=tmp_path, path=project_root, cmd="jsconfig --help")
    finally:
        execute_spin(yaml=yaml, env=tmp_path, path=project_root, cmd="cleanup")
        assert not (project_root / "jsconfig.json").exists()
