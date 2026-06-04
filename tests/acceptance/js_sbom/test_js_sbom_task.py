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
#

"""Module implementing acceptance tests for the js_sbom plugin."""

import shlex
import subprocess
import sys
import sysconfig

import pytest
from path import Path

_PLATFORM_TAG = sysconfig.get_platform().replace("-", "_")


def execute_spin(yaml, env, path, cmd=""):
    """Execute spin and return its output."""
    args = shlex.split(
        f"spin -q -p spin.data={env} -C {path} --env {env} -f {yaml} {cmd}",
        posix=sys.platform != "win32",
    )
    try:
        return subprocess.check_output(
            args, encoding="utf-8", stderr=subprocess.PIPE
        ).strip()
    except subprocess.CalledProcessError as ex:
        print(ex.stdout)
        print(ex.stderr)
        raise


@pytest.mark.acceptance()
def test_js_sbom(tmp_path):
    """
    Ensure that js-sbom collects bom.json files, places them as
    *.js_sbom.cdx.json at project root, and cleanes up generated files on
    cleanup.
    """
    yaml = "spinfile.yaml"
    project_root = Path("tests/acceptance/js_sbom")

    bom_file = (
        project_root / "build" / "lib" / "myapp" / "js" / "build" / "bom" / "bom.json"
    )
    bom_file.parent.makedirs_p()
    bom_file.write_text("{}", encoding="utf-8")

    execute_spin(yaml=yaml, env=tmp_path, path=project_root, cmd="provision")
    execute_spin(yaml=yaml, env=tmp_path, path=project_root, cmd="js-sbom")
    assert (project_root / f"myapp.{_PLATFORM_TAG}.js_sbom.cdx.json").exists()

    execute_spin(yaml=yaml, env=tmp_path, path=project_root, cmd="cleanup")
    assert not (project_root / f"myapp.{_PLATFORM_TAG}.js_sbom.cdx.json").exists()
    assert not (project_root / "build").exists()
