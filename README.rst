|Latest Version| |Python| |License|

`csspin-frontend` is maintained and published by `CONTACT Software GmbH`_ and
serves plugins for frontend development of CONTACT Elements-based applications
using the `csspin`_ task runner.

The following plugins are available:

- `csspin_frontend.cypress`: Provides tasks for running Cypress tests.
- `csspin_frontend.jest`: Provides tasks for running Jest tests.
- `csspin_frontend.jsconfig`: Provides tasks for managing JavaScript
  configurations.
- `csspin_frontend.node`: Provides tasks for provisioning and managing Node.js
  and npm.

Prerequisites
-------------

`csspin` is available on PyPI and can be installed using pip, pipx or any other
Python package manager, e.g.:

.. code-block:: console

   python -m pip install csspin

Using csspin-frontend
---------------------

The `csspin-frontend` package and its plugins can be installed by defining those
within the `spinfile.yaml` configuration file of your project.

.. code-block:: yaml

    spin:
      project_name: my_project

    # To develop plugins comfortably, install the packages editable as
    # follows and add the relevant plugins to the list 'plugins' below
    plugin_packages:
      - csspin-frontend

    # The list of plugins to be used for this project.
    plugins:
      - csspin_frontend.node

    python: # Required since csspin_frontend.node depends on csspin_python.python
      version: 3.9.8

    node:
      version: 18.17.1

.. NOTE:: Assuming that `my_project` is a component based on CONTACT Elements CE16+.

If the `spinfile.yaml` is configured correctly, you can provision the project
using `spin provision`, that will automatically create a Python virtual
environment, install NodeJS and install the required dependencies.

.. _`CONTACT Software GmbH`: https://contact-software.com
.. |Python| image:: https://img.shields.io/pypi/pyversions/csspin-frontend.svg?style=flat
    :target: https://pypi.python.org/pypi/csspin_frontend/
    :alt: Supported Python Versions
.. |Latest Version| image:: http://img.shields.io/pypi/v/csspin-frontend.svg?style=flat
    :target: https://pypi.python.org/pypi/csspin-frontend/
    :alt: Latest Package Version
.. |License| image:: http://img.shields.io/pypi/l/csspin-frontend.svg?style=flat
    :target: https://www.apache.org/licenses/LICENSE-2.0.txt
    :alt: License
.. _`csspin`: https://pypi.org/project/csspin
