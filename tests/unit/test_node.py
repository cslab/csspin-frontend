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

from csspin_frontend.node import _determine_exact_node_version


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
