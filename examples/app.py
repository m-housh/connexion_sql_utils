#!/usr/bin/env python

import os
from functools import partial
import logging

import connexion

from sqlalchemy import Column, String, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from connexion_sql_utils import BaseMixin, to_json, event_func
from connexion_sql_utils import crud

# Most of this would typically be in a different module, but since
# this is just an example, I'm sticking it all into this module.

DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'postgres')


DB_URI = 'postgres+psycopg2://{user}:{password}@{host}:{port}/{db}'.format(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    db=DB_NAME
)

engine = create_engine(DB_URI)

Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine,
                 expire_on_commit=False)
)


# The only method required to complete the mixin is to add a staticmethod
# that should return a session.  This is used in the queries.
class MyBase(BaseMixin):

    # give the models an access to a session.
    @staticmethod
    def session_maker():
        return Session()


# By attaching the ``session_maker`` method to the class we now create a
# ``declarative_base`` to be used.  The ``BaseMixin`` class declares an
# ``id`` column, that is ``postgresql.UUID``.  It also has an declared attr
# for the __tablename__.  If you would to override these, they can be declared
# when create your database model
DbModel = declarative_base(cls=MyBase)


class Foo(DbModel):

    bar = Column(String(40), nullable=False)
    baz = Column(Numeric, nullable=True)

    # a method to be called to help in the conversion to json.
    @to_json('baz')
    def convert_decimal(self, val):
        if val is not None:
            logging.debug('Converting baz...')
            return float(val)
        return val

    # attach an event listener to ensure ``bar`` is only saved
    # as a lower case string.
    @staticmethod
    @event_func('before_insert', 'before_update')
    def lower_baz(mapper, connection, target):
        target.bar = str(target.bar).lower()


# CRUD methods used in ``opertionId`` field of ``swagger.yml``
# connexion needs named parameters in it's operitionId field, so you must
# declare them in the partial in order to work correctly.
get_foo = partial(crud.get, Foo, limit=None, bar=None)
post_foo = partial(crud.post, Foo, foo=None)
get_foo_id = partial(crud.get_id, Foo, foo_id=None)
put_foo = partial(crud.put, Foo, foo_id=None, foo_data=None)
delete_foo = partial(crud.delete, Foo, foo_id=None)


app = connexion.App(__name__)
app.add_api('swagger.yml')


if __name__ == '__main__':
    port = os.environ.get('APP_PORT', 8080)
    DbModel.metadata.create_all(bind=engine)
    app.run(debug=True, port=int(port))
