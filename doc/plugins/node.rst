.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
   All rights reserved.
   https://www.contact-software.com/

.. _spin_frontend.node:

==================
spin_frontend.node
==================

The ``spin_frontend.node`` plugin provides a way to provision and
run `Node.js <https://nodejs.org/>`_ as well as the
`Node Package Manager NPM <https://www.npmjs.com/>`_.

How to setup the ``spin_frontend.node`` plugin?
###############################################

For using the ``spin_frontend.node`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``spin_frontend.node``

    plugin_packages:
        - spin_python
        - spin_frontend
    plugins:
        - spin_frontend.node
    python:
        version: '3.11.9'
    node:
        version: '18.17.1'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run tools provisioned by ``spin_frontend.node``?
#######################################################

After the project is provisioned, ``node`` node can be used as follows:

.. code-block:: bash
    :caption: Running tools provisioned by ``spin_frontend.node``

    spin run node # Run the Node.js REPL
    spin run npm install <package> # Install a package using NPM
    ...

How to use a local Node.js installation?
########################################

The ``spin_frontend.node`` plugin allows to use a local Node.js installation
instead of provisioning a new one. This can be done by setting the ``node.use``
property to the path of the local Node.js installation. This can be done in the
``spinfile.yaml`` or via the command line.

.. code-block:: bash
    :caption: Using a local Node.js installation

    spin -p node.use=/usr/bin/node provision
    spin -p node.use=/usr/bin/node node

How to use a mirror when provisioning Node.js?
##############################################

Sometimes it is necessary to use a mirror when provisioning Node.js. This can be
done by setting the ``node.mirror`` property to the URL of the mirror.

.. code-block:: yaml
    :caption: Using a mirror when provisioning Node.js

    ...
    node:
        version: '18.17.1'
        mirror: <the custom mirror goes here>

``spin_frontend.node`` schema reference
#######################################

.. include:: node_schemaref.rst
