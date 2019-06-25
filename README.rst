nasa-wildfires
==============

Download wildfire data from NASA satellites

Contributing
------------

Install dependencies for development.::

    $ pipenv install --dev

Run tests.::

    $ make test

Shipping new version to PyPI.::

    $ make ship


Developing the CLI
------------------

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as `[`prescribed by the Click documentation <https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration>`_. ::

    $ pip install --editable .
