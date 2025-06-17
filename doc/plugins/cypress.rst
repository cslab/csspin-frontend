.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
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

.. _csspin_frontend.cypress:

=======================
csspin_frontend.cypress
=======================

The ``csspin_frontend.cypress`` plugin provides a way to run the `cypress`_
frontend testing tool in the context of `csspin`_ to execute pre-implemented
cypress tests for CONTACT Elements instances.

It provides the ``cypress`` and ``cypress:open`` tasks which either run the
cypress test suite or opens the browser for interactive exploration.

How to setup the ``csspin_frontend.cypress`` plugin?
####################################################

For using the ``csspin_frontend.cypress`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_frontend.cypress``

    plugin_packages:
        - csspin-java     # required by spin-ce
        - csspin-ce       # required for creating a CE instance
        - csspin-python
        - csspin-frontend
    plugins:
        - csspin_frontend.cypress
    python:
        version: '3.11.9'
        index_url: <URL to retrieve CE packages from>
    node:
        version: '18.17.1'
    java:
        version: '17'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run cypress tests using ``csspin_frontend.cypress``?
###########################################################

The ``cypress``-task requires an existing CONTACT Elements instance, which can
be created by using the ``spin_ce.mkinstance`` plugin (see
`create new instance`_).

.. code-block:: bash
   :caption: Running Cypress tests against a CE instance using the cypress

   spin cypress

How to run Cypress tests as part of the "cept" workflow?
########################################################

Since Cypress tests are considered as acceptance tests, and they are part of the
"cept" workflow. Leveraging the workflow requires adding adding the
``spin_conpod`` plugin-package and activating the ``stdworkflows`` plugin (see
`spin_conpod.stdworkflows`_).

.. code-block:: yaml
   :caption: Adding the ``spin_conpod`` and ``stdworkflows`` plugin-packages to the ``spinfile.yaml``

    plugin_packages:
        - spin-conpod # FIXME: this must be csspin_workflows
        ...
    plugins:
        - spin_conpod.stdworkflows
        ...

The ``cept`` workflow can be executed by running the following command after
provision and creation of a CE instance:

.. code-block:: bash
   :caption: Running the "cept" workflow

   spin cept

``csspin_frontend.cypress`` schema reference
############################################

.. include:: cypress_schemaref.rst
