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

"""Unit tests for the js_sbom plugin"""

import json
import sysconfig
from pathlib import Path
from unittest import mock

import pytest

_PLATFORM_TAG = sysconfig.get_platform().replace("-", "_")
_REPOSITORY_URL = "https://packages.contact.de/apps/2026.2/+simple/"

# The @task decorator calls csspin.get_tree() at module load time; patch it so
# importing js_sbom doesn't require a live spin config tree.
with mock.patch("csspin.get_tree", return_value=mock.MagicMock()):
    from csspin_frontend.js_sbom import _build_js_purl, _collect_js_sboms


def _bom_json(name: str = "component", version: str = "1.2.3") -> dict:
    """Return a bom.json dict shaped like @cyclonedx/webpack-plugin's output"""
    purl = f"pkg:npm/{name}@{version}?"
    return {
        "metadata": {
            "component": {
                "name": name,
                "version": version,
                "purl": purl,
                "bom-ref": purl,
            }
        },
        "components": [
            {
                "name": "normalize.css",
                "version": "8.0.1",
                "purl": "pkg:npm/normalize.css@8.0.1",
            }
        ],
        "dependencies": [
            {"ref": purl, "dependsOn": '"pkg:npm/normalize.css@8.0.1"'},
            {"ref": "pkg:npm/normalize.css@8.0.1"},
        ],
    }


def _create_bom(root: Path, content: dict, *parts: str) -> Path:
    """Create a bom.json with the given content at build/lib/<parts>/bom.json"""
    bom_path = root / "build" / "lib"
    for part in parts:
        bom_path = bom_path / part
    bom_path.mkdir(parents=True, exist_ok=True)
    bom_file = bom_path / "bom.json"
    bom_file.write_text(json.dumps(content), encoding="utf-8")
    return bom_file


@pytest.mark.parametrize(
    "sbom_subpath, expected_dest_name",
    [
        # Single namespace, js dir stripped
        (
            ("component", "js", "build", "bom"),
            f"component.{_PLATFORM_TAG}.js_sbom.cdx.json",
        ),
        # Two-level namespace, js dir stripped
        (
            ("cs", "component", "js", "build", "bom"),
            f"cs-component.{_PLATFORM_TAG}.js_sbom.cdx.json",
        ),
        # Three-level namespace, js dir stripped
        (
            ("cs", "component", "something", "js", "build", "bom"),
            f"cs-component-something.{_PLATFORM_TAG}.js_sbom.cdx.json",
        ),
        # No js dir in path — all parts kept
        (("component", "build", "bom"), f"component.{_PLATFORM_TAG}.js_sbom.cdx.json"),
        # Multiple non-js parts before build/bom, no js dir
        (("foo", "bar", "build", "bom"), f"foo-bar.{_PLATFORM_TAG}.js_sbom.cdx.json"),
    ],
)
@mock.patch("csspin_frontend.js_sbom.info")
def test_collect_js_sboms_dest_name(
    _mock_info,
    tmp_path,
    sbom_subpath,
    expected_dest_name,
):
    """_collect_js_sboms derives the correct destination filename from the path"""
    _create_bom(tmp_path, _bom_json(), *sbom_subpath)
    _collect_js_sboms(tmp_path, _REPOSITORY_URL)
    assert (tmp_path / expected_dest_name).exists()


@mock.patch("csspin_frontend.js_sbom.info")
def test_collect_js_sboms_multiple_apps(_mock_info, tmp_path):
    """_collect_js_sboms handles multiple bom.json files"""
    _create_bom(tmp_path, _bom_json("app1"), "app1", "js", "build", "bom")
    _create_bom(tmp_path, _bom_json("app2"), "app2", "js", "build", "bom")

    _collect_js_sboms(tmp_path, _REPOSITORY_URL)

    assert (tmp_path / f"app1.{_PLATFORM_TAG}.js_sbom.cdx.json").exists()
    assert (tmp_path / f"app2.{_PLATFORM_TAG}.js_sbom.cdx.json").exists()


@mock.patch("csspin_frontend.js_sbom.info")
def test_collect_js_sboms_no_boms(_mock_info, tmp_path):
    """_collect_js_sboms does nothing when no bom.json files exist"""
    (tmp_path / "build" / "lib").mkdir(parents=True)

    _collect_js_sboms(tmp_path, _REPOSITORY_URL)

    assert not list(tmp_path.glob("*.js_sbom.cdx.json"))


@mock.patch("csspin_frontend.js_sbom.info")
def test_collect_js_sboms_fixes_primary_component_purl(_mock_info, tmp_path):
    """The primary component's purl gains a repository_url qualifier"""
    _create_bom(
        tmp_path, _bom_json("cs-component", "1.2.3"), "component", "js", "build", "bom"
    )

    _collect_js_sboms(tmp_path, _REPOSITORY_URL)

    dest = tmp_path / f"component.{_PLATFORM_TAG}.js_sbom.cdx.json"
    sbom_json = json.loads(dest.read_text(encoding="utf-8"))

    expected_purl = (
        "pkg:npm/cs-component@1.2.3"
        "?repository_url=https:%2F%2Fpackages.contact.de%2Fapps%2F2026.2"
    )
    assert sbom_json["metadata"]["component"]["purl"] == expected_purl
    assert sbom_json["metadata"]["component"]["bom-ref"] == expected_purl
    assert sbom_json["dependencies"] == [
        {"ref": expected_purl, "dependsOn": '"pkg:npm/normalize.css@8.0.1"'},
        {"ref": "pkg:npm/normalize.css@8.0.1"},
    ]


@mock.patch("csspin_frontend.js_sbom.info")
def test_collect_js_sboms_adds_purl_when_none_present(_mock_info, tmp_path):
    """The primary component gets a purl even if it didn't have one already"""
    content = {
        "metadata": {"component": {"name": "cs-component", "version": "1.2.3"}},
        "components": [],
        "dependencies": [],
    }
    _create_bom(tmp_path, content, "component", "js", "build", "bom")

    _collect_js_sboms(tmp_path, _REPOSITORY_URL)

    dest = tmp_path / f"component.{_PLATFORM_TAG}.js_sbom.cdx.json"
    sbom_json = json.loads(dest.read_text(encoding="utf-8"))

    assert sbom_json["metadata"]["component"]["purl"] == (
        "pkg:npm/cs-component@1.2.3"
        "?repository_url=https:%2F%2Fpackages.contact.de%2Fapps%2F2026.2"
    )


@mock.patch("csspin_frontend.js_sbom.info")
def test_collect_js_sboms_keeps_vendored_components_untouched(_mock_info, tmp_path):
    """Purls of vendored (third-party) npm components are left as-is"""
    _create_bom(tmp_path, _bom_json(), "component", "js", "build", "bom")

    _collect_js_sboms(tmp_path, _REPOSITORY_URL)

    dest = tmp_path / f"component.{_PLATFORM_TAG}.js_sbom.cdx.json"
    sbom_json = json.loads(dest.read_text(encoding="utf-8"))

    assert sbom_json["components"][0]["purl"] == "pkg:npm/normalize.css@8.0.1"


class TestBuildJsPurl:
    """Tests for _build_js_purl, the primary JS component's purl builder"""

    def test_adds_repository_url_qualifier(self):
        """Builds a plain npm purl qualified with the wheel's package index"""
        purl = _build_js_purl("cs-component", "1.2.3", _REPOSITORY_URL)
        assert purl == (
            "pkg:npm/cs-component@1.2.3"
            "?repository_url=https:%2F%2Fpackages.contact.de%2Fapps%2F2026.2"
        )

    def test_strips_credentials_from_index_url(self):
        """Never leaks basic-auth credentials into the purl"""
        purl = _build_js_purl(
            "cs-component",
            "1.2.3",
            "https://aws:abcSECRETtoken@my-domain-12345.d.codeartifact."
            "eu-central-1.amazonaws.com/pypi/my-repo/simple/",
        )
        assert purl == (
            "pkg:npm/cs-component@1.2.3"
            "?repository_url=https:%2F%2Fmy-domain-12345.d."
            "codeartifact.eu-central-1.amazonaws.com%2Fpypi%2Fmy-repo"
        )

    def test_drops_the_index_endpoint_from_repository_url(self):
        """Reduces an index URL to the repository base URL"""
        purl = _build_js_purl(
            "cs-component", "1.2.3", "https://packages.contact.de/apps/2026.2-dev/"
        )
        assert purl == (
            "pkg:npm/cs-component@1.2.3"
            "?repository_url=https:%2F%2Fpackages.contact.de%2Fapps%2F2026.2-dev"
        )

    def test_splits_a_scoped_name_into_namespace_and_name(self):
        """A '@scope/name' package name becomes the purl's namespace segment"""
        purl = _build_js_purl("@cs/component", "1.2.3", _REPOSITORY_URL)
        assert purl == (
            "pkg:npm/%40cs/component@1.2.3"
            "?repository_url=https:%2F%2Fpackages.contact.de%2Fapps%2F2026.2"
        )

    def test_unscoped_name_has_no_namespace_segment(self):
        """A plain package name has no '/' before the '@version'"""
        purl = _build_js_purl("cs-component", "1.2.3", _REPOSITORY_URL)
        assert "%40" not in purl
        assert purl.startswith("pkg:npm/cs-component@")
