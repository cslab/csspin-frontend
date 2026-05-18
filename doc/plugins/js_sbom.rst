.. -*- coding: utf-8 -*-
   Copyright (C) 2026 CONTACT Software GmbH
   https://www.contact-software.com/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

.. _csspin_frontend.js_sbom:

========================
csspin_frontend.js_sbom
========================

The ``csspin_frontend.js_sbom`` plugin provides the ``js-sbom`` task for
building Software Bill of Materials (SBOMs) for JavaScript applications based on
CONTACT Elements in CycloneDX format. It builds the project if necessary and
then collects the generated ``bom.json`` files into top-level ``*.js_sbom.cdx.json``
files named after their namespace.

How to setup the ``csspin_frontend.js_sbom`` plugin?
####################################################

For using the ``csspin_frontend.js_sbom`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_frontend.js_sbom``

    plugin_packages:
        - csspin-python
        - csspin-frontend
    plugins:
        - csspin_frontend.js_sbom
    python:
        version: '3.11.9'

The provisioning of the required virtual environment as well as the plugin
dependencies can be done via the well-known ``spin provision``-command.

How to build JavaScript SBOMs using ``csspin_frontend.js_sbom``?
################################################################

The ``js-sbom`` task builds the JavaScript application (via ``setup.py
build_js``) if no ``build/`` directory is present, then collects all
``bom/bom.json`` files from the build output and places them at the project
root, named after their namespace:

.. code-block:: bash
   :caption: Building JavaScript SBOMs

   spin js-sbom

The collected SBOMs are written as ``<namespace>.js_sbom.cdx.json`` files in the
project root. The ``build/`` directory and any ``*.cdx.json`` files are removed
by the cleanup step.

``csspin_frontend.js_sbom`` schema reference
############################################

.. include:: js_sbom_schemaref.rst
