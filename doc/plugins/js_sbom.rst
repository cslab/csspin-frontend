.. -*- coding: utf-8 -*-
   Copyright (C) 2026 CONTACT Software GmbH
   https://www.contact-software.com/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0

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
CONTACT Elements in CycloneDX format. It generates the ``bom.json`` files if
necessary and then collects them into top-level ``*.js_sbom.cdx.json`` files
named after the application's path.

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
    contact_elements:
        umbrella: '2027.1'
    python:
        version: '3.11.9'

The provisioning of the required virtual environment as well as the plugin
dependencies can be done via the well-known ``spin provision``-command.

How to build JavaScript SBOMs using ``csspin_frontend.js_sbom``?
################################################################

.. code-block:: bash
   :caption: Building JavaScript SBOMs

   spin js-sbom

How the ``bom.json`` files are generated depends on
``contact_elements.umbrella``, because the JavaScript build stopped emitting
them with CONTACT Elements 2027.1:

* For ``16.0``, ``2026.1`` and ``2026.2`` the build writes them itself, so the
  task runs ``setup.py build_js`` unless a ``build/`` directory is already
  present, and then collects the ``bom/bom.json`` files below ``build/lib``.
* For ``2027.1`` and later the task runs ``webmake sbom <project name>``, which
  writes each application's ``bom.json`` to ``<application>/build/bom/``, and
  then collects those.

The collected SBOMs are written as
``<application path>.<platform tag>.js_sbom.cdx.json`` files in the project
root, e.g. ``cs-variants-web-editor.linux_x86_64.js_sbom.cdx.json``. The
``build/`` directory and any ``*.cdx.json`` files are removed by the cleanup
step.

``csspin_frontend.js_sbom`` schema reference
############################################

.. include:: js_sbom_schemaref.rst
