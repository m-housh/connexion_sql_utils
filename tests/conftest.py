import pytest
import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from connexion_sql_utils import BaseMixin, post

DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'postgres')


URI = 'postgres+psycopg2://{user}:{password}@{host}:{port}/{db}'.format(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    db=DB_NAME
)

engine = create_engine(URI)

Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine,
                 expire_on_commit=False)
)

session = Session()


class MyBase(BaseMixin):

    @staticmethod
    def session_maker():
        return session


Base = declarative_base(cls=MyBase)


class Foo(Base):

    bar = Column(String(), nullable=True)


@pytest.fixture(scope='module', autouse=True)
def create_all():
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def drop_all():
    def inner():
        Base.metadata.drop_all(bind=engine)
    return inner


@pytest.fixture()
def create_tables():
    def inner():
        return Base.metadata.create_all(bind=engine)
    return inner


@pytest.fixture(scope='session', autouse=True)
def create():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    for i in range(10):
        post(Foo, foo={'bar': 'baz-{}'.format(i)})
