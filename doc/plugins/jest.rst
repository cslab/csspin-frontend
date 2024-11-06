.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
   All rights reserved.
   https://www.contact-software.com/

.. _spin_frontend.jest:

==================
spin_frontend.jest
==================

``spin_frontend.jest`` is a plugin that provides a task to run `Jest`_ tests for
the current project. It requires one or more ``jest.config.json`` (or
``jest.config.js``) files to be present in the project source tree.

The Jest plugin does not install Jest from npm, but uses the webmake of an
existing instance.

The ``jest`` task is part of the "test" workflow and can be leveraged by
importing making use of `spin_conpod.stdworkflows`_.

How to setup the ``spin_frontend.jest`` plugin?
###############################################

For using the ``spin_frontend.jsconfig`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``spin_frontend.jsconfig``

    plugin_packages:
        - spin_ce
        - spin_frontend
        - spin_python
    plugins:
        - spin_ce.mkinstance
        - spin_frontend.jest
    python:
        version: '3.11.9'
        index_url: https://packages.contact.de/apps/16.0-dev/+simple/
    node:
        version: '18.20.0'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run the ``jest`` task using ``spin_frontend.jest``?
##########################################################

The ``jest`` requires the existence of a CE instance (see `create new
instance`_).

.. code-block:: bash
   :caption: Running jest tests using the ``jest`` plugin

   spin jest

Collecting coverage is as simple as running the ``jest`` task with the
``--coverage`` option.

.. code-block:: bash
   :caption: Collecting coverage using the ``jest`` plugin

   spin jest --coverage

How to run jest tests as part of the "test" workflow?
#####################################################

The ``jest`` task is part of the "test" workflow and can be executed by running
the following command, assuming that the CE instance is already created and
`spin_conpod.stdworkflows`_ is configured as follows:

.. code-block:: yaml
   :caption: Adding the ``spin_conpod`` and ``stdworkflows`` plugin-packages to the ``spinfile.yaml``

    plugin_packages:
        - spin_conpod
        ...
    plugins:
        - spin_conpod.stdworkflows
        ...

The ``test`` workflow can be executed by running the following command after
provision and creation of a CE instance:

.. code-block:: bash
   :caption: Running the "test" workflow

   spin test

How to debug jest tests using ``spin_frontend.jest``?
#####################################################

The ``jest`` task supports the ``--debug`` option to run the tests in debug
mode, which starts listening and waits for a debugger to attach.

``spin_frontend.jest`` schema reference
#######################################

.. include:: jest_schemaref.rst
