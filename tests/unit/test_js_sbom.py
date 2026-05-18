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

from pathlib import Path
from unittest import mock

import pytest

# The @task decorator calls csspin.get_tree() at module load time; patch it so
# importing js_sbom doesn't require a live spin config tree.
with mock.patch("csspin.get_tree", return_value=mock.MagicMock()):
    from csspin_frontend.js_sbom import _collect_js_sboms


def _create_bom(root: Path, *parts: str) -> Path:
    """Create a dummy bom.json at build/lib/<parts>/bom.json"""
    bom_path = root / "build" / "lib"
    for part in parts:
        bom_path = bom_path / part
    bom_path.mkdir(parents=True, exist_ok=True)
    bom_file = bom_path / "bom.json"
    bom_file.write_text("{}", encoding="utf-8")
    return bom_file


@pytest.mark.parametrize(
    "sbom_subpath, expected_dest_name",
    [
        # Single namespace, js dir stripped
        (("component", "js", "build", "bom"), "component.js_sbom.cdx.json"),
        # Two-level namespace, js dir stripped
        (("cs", "component", "js", "build", "bom"), "cs-component.js_sbom.cdx.json"),
        # Three-level namespace, js dir stripped
        (
            ("cs", "component", "something", "js", "build", "bom"),
            "cs-component-something.js_sbom.cdx.json",
        ),
        # No js dir in path — all parts kept
        (("component", "build", "bom"), "component.js_sbom.cdx.json"),
        # Multiple non-js parts before build/bom, no js dir
        (("foo", "bar", "build", "bom"), "foo-bar.js_sbom.cdx.json"),
    ],
)
@mock.patch("csspin_frontend.js_sbom.info")
@mock.patch("csspin_frontend.js_sbom.copy")
def test_collect_js_sboms_dest_name(
    mock_copy,
    _mock_info,
    tmp_path,
    sbom_subpath,
    expected_dest_name,
):
    """_collect_js_sboms derives the correct destination filename from the path"""
    _create_bom(tmp_path, *sbom_subpath)

    _collect_js_sboms(tmp_path)

    mock_copy.assert_called_once()
    _, dest = mock_copy.call_args.args
    assert dest == tmp_path / expected_dest_name


@mock.patch("csspin_frontend.js_sbom.info")
@mock.patch("csspin_frontend.js_sbom.copy")
def test_collect_js_sboms_copies_correct_source(_mock_copy, _mock_info, tmp_path):
    """_collect_js_sboms passes the actual bom.json path as the copy source"""
    bom_file = _create_bom(tmp_path, "component", "js", "build", "bom")

    _collect_js_sboms(tmp_path)

    src, _ = _mock_copy.call_args.args
    assert src == bom_file


@mock.patch("csspin_frontend.js_sbom.info")
@mock.patch("csspin_frontend.js_sbom.copy")
def test_collect_js_sboms_multiple_apps(_mock_copy, _mock_info, tmp_path):
    """_collect_js_sboms handles multiple bom.json files"""
    _create_bom(tmp_path, "app1", "js", "build", "bom")
    _create_bom(tmp_path, "app2", "js", "build", "bom")

    _collect_js_sboms(tmp_path)

    assert _mock_copy.call_count == 2
    dest_names = {call.args[1].name for call in _mock_copy.call_args_list}
    assert dest_names == {"app1.js_sbom.cdx.json", "app2.js_sbom.cdx.json"}


@mock.patch("csspin_frontend.js_sbom.info")
@mock.patch("csspin_frontend.js_sbom.copy")
def test_collect_js_sboms_no_boms(_mock_copy, _mock_info, tmp_path):
    """_collect_js_sboms does nothing when no bom.json files exist"""
    (tmp_path / "build" / "lib").mkdir(parents=True)

    _collect_js_sboms(tmp_path)
    _mock_copy.assert_not_called()
