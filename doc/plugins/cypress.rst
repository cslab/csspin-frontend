.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
   All rights reserved.
   https://www.contact-software.com/

.. _spin_frontend.cypress:

=====================
spin_frontend.cypress
=====================

The ``spin_frontend.cypress`` plugin provides a way to run the `cypress
<https://www.cypress.io/>`_ frontend testing tool in the context of cs.spin to
execute pre-implemented cypress tests for CONTACT Elements instances.

It provides the ``cypress`` and ``cypress:open`` tasks which either run the
cypress test suite or opens the browser for interactive exploration.

How to setup the ``spin_frontend.cypress`` plugin?
##################################################

For using the ``spin_frontend.cypress`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``spin_frontend.cypress``

    plugin_packages:
        - spin_ce # required for creating a CE instance
        - spin_python
        - spin_frontend
    plugins:
        - spin_frontend.cypress
    python:
        version: '3.11.9'
        index_url: <the index URL to retrieve cs.platform as dependency of spin_ce>
    node:
        version: '18.17.1'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run cypress tests using ``spin_frontend.cypress``?
#########################################################

The ``cypress``-task requires an existing CONTACT Elements instance, which can
be created by using the ``spin_ce.mkinstance`` plugin.

.. TODO: Add documentation pointing to spin_ce.mkinstance

.. code-block:: bash
   :caption: Running Cypress tests against a CE instance using the cypress

   spin cypress

How to run Cypress tests as part of the "cept" workflow?
########################################################

Since Cypress tests are considered as acceptance tests, and they are part of the
"cept" workflow. Leveraging the workflow requires adding adding the
``spin_conpod`` plugin-package and activating the ``stdworkflows`` plugin.

.. code-block:: yaml
   :caption: Adding the ``spin_conpod`` and ``stdworkflows`` plugin-packages to the ``spinfile.yaml``

    plugin_packages:
        - spin_conpod
        ...
    plugins:
        - spin_conpod.stdworkflows
        ...

The ``cept`` workflow can be executed by running the following command after
provision and creation of a CE instance:

.. code-block:: bash
   :caption: Running the "cept" workflow

   spin cept

.. TODO: add link to documentation of spin_conpod.stdworkflows


``spin_frontend.cypress`` schema reference
##########################################

.. include:: cypress_schemaref.rst
