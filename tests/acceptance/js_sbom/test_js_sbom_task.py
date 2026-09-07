# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2026 CONTACT Software GmbH
# https://www.contact-software.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Module implementing acceptance tests for the js_sbom plugin."""

import json
import shlex
import subprocess
import sys
import sysconfig

import pytest

_PLATFORM_TAG = sysconfig.get_platform().replace("-", "_")

# What the fixture project's bom.json describes, mirroring fake_webmake.BOM_JSON
# so both code paths have to yield the same SBOM.
_BOM_JSON = {
    "metadata": {
        "component": {
            "name": "myapp",
            "version": "1.0.0",
            "purl": "pkg:npm/myapp@1.0.0",
            "bom-ref": "pkg:npm/myapp@1.0.0",
        }
    },
    "dependencies": [{"ref": "pkg:npm/myapp@1.0.0"}],
}


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
@pytest.mark.parametrize("umbrella", ("2026.2", "2027.1"))
def test_js_sbom(spin_env, project_root, umbrella):
    """
    Ensure that js-sbom places the same *.js_sbom.cdx.json at the project root
    for both generation paths, and cleans up generated files on cleanup.
    """
    yaml = "spinfile.yaml"
    webmake_bom_dir = project_root / "myapp" / "js" / "build" / "bom"

    if umbrella == "2026.2":
        # Up to 2026.2 the bom.json is a by-product of the JavaScript build.
        # Providing it upfront makes js-sbom skip 'setup.py build_js'.
        legacy_bom_dir = (
            project_root / "build" / "lib" / "myapp" / "js" / "build" / "bom"
        )
        legacy_bom_dir.makedirs_p()
        (legacy_bom_dir / "bom.json").write_text(
            json.dumps(_BOM_JSON), encoding="utf-8"
        )

    execute_spin(yaml=yaml, env=spin_env, path=project_root, cmd="provision")
    execute_spin(
        yaml=yaml,
        env=spin_env,
        path=project_root,
        cmd=f"-p contact_elements.umbrella={umbrella} js-sbom",
    )

    if umbrella == "2027.1":
        # From 2027.1 on, js-sbom has to trigger the generation itself.
        argv = json.loads((webmake_bom_dir / "argv.json").read_text(encoding="utf-8"))
        assert argv == ["sbom", "myapp"]
    else:
        assert not webmake_bom_dir.exists(), "webmake must not run before 2027.1"

    sbom_file = project_root / f"myapp.{_PLATFORM_TAG}.js_sbom.cdx.json"
    assert sbom_file.exists()

    sbom_json = json.loads(sbom_file.read_text(encoding="utf-8"))
    purl = sbom_json["metadata"]["component"]["purl"]
    assert purl == "pkg:npm/myapp@1.0.0?repository_url=https:%2F%2Fpypi.org"

    execute_spin(yaml=yaml, env=spin_env, path=project_root, cmd="cleanup")
    assert not sbom_file.exists()
    assert not (project_root / "build").exists()
