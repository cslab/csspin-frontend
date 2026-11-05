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

.. _csspin_frontend.node:

====================
csspin_frontend.node
====================

The ``csspin_frontend.node`` plugin provides a way to provision and
run `Node.js`_ as well as the Node Package Manager `npm`_.

How to setup the ``csspin_frontend.node`` plugin?
#################################################

For using the ``csspin_frontend.node`` plugin, a project's ``spinfile.yaml``
must at least contain the following configuration.

.. code-block:: yaml
    :caption: Minimal configuration of ``spinfile.yaml`` to use ``csspin_frontend.node``

    plugin_packages:
        - csspin-python
        - csspin-frontend
    plugins:
        - csspin_frontend.node
    contact_elements:
        umbrella: '2026.2'
    python:
        version: '3.11.9'
    node:
        version: '24'

The provisioning of the required virtual environment as well as the plugins
dependencies can be done via the well-known ``spin provision``-command.

How to run tools provisioned by ``csspin_frontend.node``?
#########################################################

After the project is provisioned, ``node`` node can be used as follows:

.. code-block:: bash
    :caption: Running tools provisioned by ``csspin_frontend.node``

    spin run node # Run the Node.js REPL
    spin run npm install <package> # Install a package using NPM
    ...

How to use a local Node.js installation?
########################################

The ``csspin_frontend.node`` plugin allows to use a local Node.js installation
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
        version: '24'
        mirror: <the custom mirror goes here>

.. note::

    The URL that ``node.mirror`` points to must behave the same as
    https://nodejs.org/dist/.

    The mirror is not contacted if ``node.use`` is set.

How to use a registry or mirror for npm and Yarn packages?
##########################################################

By default, npm and Yarn fetch packages from the public registries. How to point
them elsewhere depends on the umbrella release (``contact_elements.umbrella``).
The Node.js download uses ``node.mirror`` in both cases.

Umbrella 2026.1 and 2026.2
--------------------------

These releases use Yarn classic. Its lock files pin packages to URLs of the
public registry, which ``node.registry_url`` cannot redirect. Set
``node.yarn_offline_mirror`` to a directory of package tarballs instead. Yarn
reads pinned packages from it before asking a registry.

.. code-block:: yaml

    contact_elements:
        umbrella: '2026.2'
    node:
        version: '24'
        yarn_offline_mirror: <the directory of the tarballs goes here>

- The directory has to exist before ``spin provision``, which stops with an
  error otherwise. A relative path resolves against the project root and ``~``
  expands to the home directory.
- Yarn saves every tarball it downloads in the directory, so it has to be
  writable. To fill it, run the project's Yarn installs once with access to the
  public registries.
- Yarn requests a tarball missing from the directory from its pinned URL, which
  fails on a machine without access to that registry.
- Packages that no lock file pins still need ``node.registry_url``, for example
  the reporter that the jest plugin installs with ``--with-test-report``.

Umbrella 2027.1 and later
-------------------------

These releases use Yarn Berry. Their lock files contain no registry URLs, so
``node.registry_url`` covers npm and Yarn. The URL may use http or https. The
plugin ignores ``node.yarn_offline_mirror`` and prints a warning.

.. code-block:: yaml

    contact_elements:
        umbrella: '2027.1'
    node:
        version: '26'
        registry_url: <the URL of the registry goes here>

``csspin_frontend.node`` schema reference
#########################################

.. include:: node_schemaref.rst
