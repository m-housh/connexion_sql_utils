===============================
Connexion Sqlalchemy Utils
===============================

.. image:: https://img.shields.io/pypi/v/connexion_sql_utils.svg
    :target: https://pypi.python.org/pypi/connexion_sql_utils

.. image:: https://img.shields.io/travis/m-housh/connexion_sql_utils.svg
    :target: https://travis-ci.org/m-housh/connexion_sql_utils

.. image:: https://coveralls.io/repos/github/m-housh/connexion_sql_utils/badge.svg?branch=master
    :target: https://coveralls.io/github/m-housh/connexion_sql_utils?branch=master

.. image:: https://readthedocs.org/projects/connexion_sql_utils/badge/?version=latest
    :target: https://connexion-sql-utils.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


Sqlalchemy, Postgres, Connexion utility


* Documentation: https://connexion-sql-utils.readthedocs.io.


Features
--------

* Helps create REST api's quickly with ``Connexion``, ``Sqlalchemy``,
  and ``Postgresql``


Running example api in Docker
------------------------------

By cloning the repo:
    
.. code-block:: bash

    git clone https://github.com/m-housh/connexion_sql_utils.git

    cd ./connexion_sql_utils

    docker-compose up

Without cloning the repo:

.. code-block:: bash

    docker pull mhoush/connexion_sql_utils
    docker pull postgres/alpine

    docker run -d --name some_postgres \
        -e POSTGRES_PASSWORD=postgres \
        postgres:alpine

    docker run --rm -it --link some_postgres:postgres \
        -e DB_HOST=postgres \
        -e DB_PASSWORD=postgres \
        -p "8080:8080" \
        mhoush/connexion_sql_utils

Check out the example api at ``http://localhost:8080/ui``


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

