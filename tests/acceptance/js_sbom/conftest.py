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

"""Fixtures for the js_sbom acceptance tests"""

import pytest
from path import Path


@pytest.fixture(scope="module")
def spin_env(tmp_path_factory):
    """One spin environment shared by all parametrizations of a test.

    Provisioning builds a CPython from source, which is not worth repeating
    for every umbrella release under test.
    """
    return tmp_path_factory.mktemp("spin_env")


@pytest.fixture()
def project_root():
    """The fixture project's root, cleaned of generated files afterwards."""
    root = Path(__file__).parent
    yield root
    (root / "build").rmtree_p()
    (root / "myapp").rmtree_p()
    for sbom_file in root.glob("*.js_sbom.cdx.json"):
        sbom_file.remove()
