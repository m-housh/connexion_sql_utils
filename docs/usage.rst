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



