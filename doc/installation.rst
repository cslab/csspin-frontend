.. -*- coding: utf-8 -*-
   Copyright (C) 2024 CONTACT Software GmbH
   All rights reserved.
   https://www.contact-software.com/

======================
Installation and setup
======================

cs.spin must be installed beforehand, this can be done as documented at
http://qs.pages.contact.de/spin/cs.spin/installation.html.

For leveraging plugins from within the ``spin_frontend`` plugin-package for
``cs.spin``, the plugin-package must be added to the list of plugin-packages
within a project's ``spinfile.yaml``.

.. code-block:: yaml
    :caption: Example: ``spinfile.yaml`` setup to enable the pytest and python plugins

    plugin_packages:
        - spin_ce # required by spin_frontend.cypress
        - spin_python # required by spin_frontend
        - spin_frontend
    plugins:
        - spin_frontend:
            - cypress
            - jsconfig
            - node
    python:
        version: "3.11.9"
        # The index-url must be set in order to install spin_ce's dependencies
        index_url: https://packages.contact.de/apps/16.0-dev/+simple/
    node:
        version: 18.17.1

After the setup is done, the plugin-package can be provisioned by executing the
following command within the project's directory:

.. code-block:: console

    spin provision

The plugins and their tasks defined in the plugins section of the
``spinfile.yaml`` can now be used:

.. code-block:: console

    spin jsconfig --help
