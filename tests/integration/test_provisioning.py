# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2021 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Module implementing the integration tests for spin_frontend"""

from os.path import join

import pytest
from spin import backtick, cli


@pytest.fixture(autouse=True)
def cfg():
    """Fixture creating the configuration tree"""
    cli.load_config_tree(None)


def do_test(tmpdir, what, cmd, path="tests/integration"):
    """Helper to execute spin calls via spin."""
    output = backtick(
        f"spin -p spin.cache={tmpdir} -q -C {path} --env {tmpdir} -f"
        f" {what} --cleanup --provision {cmd}"
    )
    output = output.strip()
    return output


@pytest.mark.integration()
def test_node(tmpdir):
    """Provisioning the node plugin"""
    assert do_test(
        tmpdir=tmpdir,
        what=join("tests", "integration", "yamls", "node.yaml"),
        cmd="run node --version",
    ).endswith("v18.17.1")
