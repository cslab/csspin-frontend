.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
   All rights reserved.
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

.. _csspin_frontend.jsconfig:

========================
csspin_frontend.jsconfig
========================

``csspin_frontend.jsconfig`` is a plugin that provides a task to create a
`jsconfig.json`_ file
for a project. This file can be interpreted by IDEs like Visual Studio Code to
provide better IntelliSense support for JavaScript and TypeScript projects.

How to setup the ``csspin_frontend.jsconfig`` plugin?
#####################################################

For using the ``csspin_frontend.jsconfig`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_frontend.jsconfig``

    plugin_packages:
        - csspin-python
        - csspin-frontend
    plugins:
        - csspin_frontend.jsconfig
    python:
        version: '3.11.9'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run the ``jsconfig`` task using ``csspin_frontend.jsconfig``?
####################################################################

After the project is provisioned, the ``jsconfig`` task can be run to create a
``jsconfig.json`` file in the project root:

.. code-block:: bash
   :caption: Running the jsconfig task

   spin jsconfig

``csspin_frontend.jsconfig`` schema reference
###########################################

.. include:: jsconfig_schemaref.rst
