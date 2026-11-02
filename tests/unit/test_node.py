# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2025 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Module implementing the unit tests for csspin_python"""

import json
from unittest import mock

import pytest
from click import Abort
from path import Path

from csspin_frontend.node import _determine_exact_node_version, _node_archive_name


@pytest.fixture(scope="session")
def mock__fetch_node_dist_index():
    """
    Return the checked-in testdata
    """
    test_data_file = (
        Path(__file__).parent / "test_data" / "node_dist_index_response.json"
    )
    with mock.patch(
        "csspin_frontend.node._fetch_node_dist_index"
    ) as node_dist_index_mock:
        with open(test_data_file, encoding="utf-8") as fd:
            node_dist_index_mock.return_value = json.load(fd)
            yield


@pytest.mark.parametrize(
    "version_string, expected_version",
    (
        ("lts", "v22.17.1"),
        ("LTS", "v22.17.1"),
        ("20", "v20.19.4"),
        ("20.18", "v20.18.3"),
        ("20.18.1", "v20.18.1"),
        ("v20", "v20.19.4"),
        ("v20.18", "v20.18.3"),
        ("v20.18.1", "v20.18.1"),
    ),
)
@pytest.mark.usefixtures("mock__fetch_node_dist_index")
def test__determine_exact_node_version(version_string, expected_version):
    """
    Check whether determining the node version works.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = version_string
    assert _determine_exact_node_version(cfg_mock) == expected_version


@pytest.mark.parametrize("version_string", ("99.1.2", "v99.1.2"))
def test__determine_exact_node_version_exact_version_needs_no_index(version_string):
    """
    Check whether an exact version is returned without requesting the node index.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = version_string
    with mock.patch("csspin_frontend.node._fetch_node_dist_index") as index_mock:
        assert _determine_exact_node_version(cfg_mock) == "v99.1.2"
    index_mock.assert_not_called()


@pytest.mark.parametrize(
    "version_string",
    (
        ("foo"),
        ("vfoo"),
    ),
)
@pytest.mark.usefixtures("mock__fetch_node_dist_index")
def test__determine_exact_node_version_error(version_string):
    """
    Test whether determining the node version `die`s when the version cannot be
    found.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = version_string
    with pytest.raises(Abort):
        assert _determine_exact_node_version(cfg_mock)


@pytest.mark.parametrize(
    "sys_platform, machine, expected",
    (
        ("linux", "x86_64", ("node-v22.17.1-linux-x64", ".tar.xz")),
        ("linux", "aarch64", ("node-v22.17.1-linux-arm64", ".tar.xz")),
        ("linux", "armv7l", ("node-v22.17.1-linux-armv7l", ".tar.xz")),
        ("darwin", "x86_64", ("node-v22.17.1-darwin-x64", ".tar.xz")),
        ("darwin", "arm64", ("node-v22.17.1-darwin-arm64", ".tar.xz")),
        ("win32", "AMD64", ("node-v22.17.1-win-x64", ".zip")),
        ("win32", "ARM64", ("node-v22.17.1-win-arm64", ".zip")),
    ),
)
def test__node_archive_name(sys_platform, machine, expected):
    """
    Check whether the Node.js archive matching the platform and machine
    architecture is chosen.
    """
    with (
        mock.patch("csspin_frontend.node.sys.platform", sys_platform),
        mock.patch("csspin_frontend.node.platform.machine", return_value=machine),
    ):
        assert _node_archive_name("v22.17.1") == expected
