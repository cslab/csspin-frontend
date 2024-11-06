.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
   All rights reserved.
   https://www.contact-software.com/

.. _spin_frontend.jsconfig:

======================
spin_frontend.jsconfig
======================

``spin_frontend.jsconfig`` is a plugin that provides a task to create a
`jsconfig.json`_ file
for a project. This file can be interpreted by IDEs like Visual Studio Code to
provide better IntelliSense support for JavaScript and TypeScript projects.

How to setup the ``spin_frontend.jsconfig`` plugin?
###################################################

For using the ``spin_frontend.jsconfig`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``spin_frontend.jsconfig``

    plugin_packages:
        - spin_python
        - spin_frontend
    plugins:
        - spin_frontend.jsconfig
    python:
        version: '3.11.9'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run the ``jsconfig`` task using ``spin_frontend.jsconfig``?
##################################################################

After the project is provisioned, the ``jsconfig`` task can be run to create a
``jsconfig.json`` file in the project root:

.. code-block:: bash
   :caption: Running the jsconfig task

   spin jsconfig

``spin_frontend.jsconfig`` schema reference
###########################################

.. include:: jsconfig_schemaref.rst
