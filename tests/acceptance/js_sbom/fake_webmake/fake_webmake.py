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

"""Stand-in for cs.webmake's "webmake" command line interface.

Writes a bom.json where the real ``webmake sbom`` writes it, at
``<app>/build/bom/bom.json`` below the project root, and records its arguments
next to it so the acceptance test can assert on the invocation. The component
name and version must match what test_js_sbom_task.py expects.
"""

import json
import os
import sys

APP_DIR = os.path.join("myapp", "js")
BOM_JSON = {
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


def main() -> None:
    """Record the arguments and write the bom.json the real webmake would"""
    bom_dir = os.path.join(os.getcwd(), APP_DIR, "build", "bom")
    os.makedirs(bom_dir, exist_ok=True)
    with open(os.path.join(bom_dir, "argv.json"), "w", encoding="utf-8") as fd:
        json.dump(sys.argv[1:], fd)
    with open(os.path.join(bom_dir, "bom.json"), "w", encoding="utf-8") as fd:
        json.dump(BOM_JSON, fd)
