# -*- coding: utf-8 -*-
"""
abc
---

    This module contains an abc class that can be used to check that the
    correct interface is defined to use the ``crud`` methods.  Nothing
    actually inherits from this class as it breaks when making an
    ``sqlalchemy.ext.declarative:declarative_base``, but it is helpful
    for ``issubclass`` and ``isinstance`` checks.


    When inheriting from this package's :class:`BaseMixin` then one only
    needs to implement a ``session_maker`` method.


"""
import abc
import contextlib


def _check_mro(Cls, key) -> bool:
    """Helper to check the mro for a class for the given method/attribute name

    :param Cls:  The class to check
    :param key:  The attribute name to check for in the ``__mro__``

    """
    check = any(key in Base.__dict__ for Base in Cls.__mro__ if
                hasattr(Base, '__dict__'))
    return check


class BaseMixinABC(metaclass=abc.ABCMeta):
    """Used to test validity of a mixin.  The mixin can not directly inherit
    from this abc class because of inheritance conflicts with sqlalchemy's
    declarative base class, however if a mixin declares all the required
    methods, then it will pass an ``isinstance`` or an ``issubclass`` check.

    The mixin in this package declares all of the methods except the
    ``session_maker`` method which should be implemented once you create
    a ``sqlalchemy.orm.sessionmaker``

    Example::

        engine = create_engine(DB_URI)
        session = scoped_session(sessionmaker(bind=engine))

        class MyBase(BaseMixin):

            @staticmethod
            def session_maker():
                return session()


        DbModel = declarative_base(cls=MyBase)
        assert issubclass(DbModel, BaseMixinABC)  #  True


    Then all of your sqlalchemy models could inherit from the ``DbModel``.

    """
    @staticmethod
    @abc.abstractmethod
    def session_maker():  # pragma: no cover
        """Return an :class:`sqlalchemy.orm.Session` to be used in the other
        methods.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def query_by(cls, **kwargs):  # pragma: no cover
        """Query the database model with the given criteria.

        This is used as you would use ``filter_by`` on an sqlalchemy query.
        And should always return a list of items.

        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_id(cls, id):  # pragma: no cover
        """Query the database for a single item by it's unique id.

        """
        pass

    @abc.abstractmethod
    def save(self):  # pragma: no cover
        """Save an instance to the database.

        """
        pass

    @abc.abstractmethod
    def update(self, **kwargs):  # pragma: no cover
        """Update an instance's attributes and save to the database.

        """
        pass

    @abc.abstractmethod
    def delete(self):  # pragma: no cover
        """Delete an instance from the database.

        """
        pass

    @abc.abstractmethod
    def dump(self):  # pragma: no cover
        """Return a json representation of the instance.  This is also used
        as the str() representation of an instance.

        """
        pass

    @abc.abstractmethod
    def _asDict(self):  # pragma: no cover
        """Create a dict representation of an instance, this is typically used
        to create the json representation.

        """
        pass

    @classmethod
    @contextlib.contextmanager
    @abc.abstractmethod
    def session_scope(cls):  # pragma: no cover
        """A context manager for a session, should yield a
        :class:`sqlalchemy.orm.Session`

        """
        yield

    def __str__(self) -> str:
        """Return a json representation.

        """
        return self.dump()

    @classmethod
    def __subclasshook__(cls, Cls):
        if cls is BaseMixinABC:
            check_keys = ('query_by', 'get_id', 'delete', 'update', 'save',
                          'session_scope', '_asDict', 'dump', 'session_maker')

            if all(map(lambda x: _check_mro(Cls, x), check_keys)):
                return True

        return NotImplemented
