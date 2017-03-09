=====
Usage
=====

To use Connexion Sqlalchemy Utils in a project::

    import connexion_sql_utils


This package is meant to be used in conjunction with ``Connexion`` which 
utilizes an API first approach to building REST API's for micro-services.

.. seealso:: http://connexion.readthedocs.io


This package has an Sqlalchemy Mixin used with Postgresql to create a 
declarative base, which can then be used to declare your database models.

This package also has a set of utility functions that when combined with
``functools.partial`` can be used to quickly create the routes for the
api.


*app.py:*

.. literalinclude:: ../examples/app.py
    

*swagger.yml:*

.. literalinclude:: ../examples/swagger.yml
    :language: yaml


You can run this example locally in a docker container.

.. code-block:: bash

    git-clone https://github.com/m-housh/connexion_sql_utils.git
    cd ./connexion_sql_utils

**and**

.. code-block:: bash

    docker-compose build
    docker-compose up -d db  # db needs a few seconds to start-up
    docker-compose up api

**or**

.. code-block:: bash

    make examples
    

You can then visit ``http://localhost:8080/ui`` to view the swagger docs and
try it out.

