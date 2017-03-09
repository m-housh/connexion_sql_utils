from typing import Dict, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event
from sqlalchemy.ext.declarative import declared_attr

import uuid

import contextlib
import json
import logging

from .base_mixin_abc import BaseMixinABC
from .decorators import event_func

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _quote_if_str(string):
    """Used in the repr method to quote a string attribute.

    """
    if isinstance(string, str):
        return "'{}'".format(string)
    return string


class BaseMixin(object):
    """Base sqlalchemy mixin.  Adds id column as a postgresql.UUID column,
    and will create the uuid before saving to the database.

    A user must define a ``session_maker`` on the mixin, to
    complete it as a classmethod or a staticmethod.

    All query methods, automatically create a session from the ``session_maker``
    method that should be declared on a sub-class.  Any method that creates,
    updates, or deletes automatically adds and commits the changes.

    """
    id = Column(UUID(), primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @staticmethod
    @event_func('before_insert')
    def create_id(mapper, connection, target):
        """Automatically creates a ``UUID`` before inserting a new
        item.

        """
        target.id = str(uuid.uuid4())

    @classmethod
    def __declare_last__(cls):  # pragma: no cover
        event_funcs = (getattr(cls, f) for f in dir(cls) if
                       getattr(getattr(cls, f), '_event_func', False) is True)

        for fn in event_funcs:
            for ename in fn._event_names:
                event.listen(cls, ename, fn)

    @classmethod
    def query_by(cls, **kwargs):
        """Return a query statement for the class.

        This would be simalar to::

            >>> session.query(MyDbModel).filter_by(id=1234)

        """
        with cls.session_scope() as session:
            return session.query(cls).filter_by(**kwargs)

    @classmethod
    def get_id(cls, id):
        """Get by id.

        :param id:  The unique identifier for the class.

        This is would be like::

            >>> session.query(MyDbModel).filter_by(id=1234).first()

        """
        try:
            return cls.query_by(id=id).first()
        except:
            return None

    def update(self, **kwargs):
        """Update attributes on an instance.

        :param kwargs:  The attributes to update on the instance.  Any
                        attribute not declared on the class is ignored.

        """
        with self.session_scope() as session:
            for key in (k for k in vars(self.__class__)
                        if not k.startswith('_')):
                if kwargs.get(key, None) is not None:
                    setattr(self, key, kwargs[key])
            session.add(self)

    def save(self):
        """Save an instance to the database.

        """
        with self.session_scope() as session:
            session.add(self)

    def delete(self):
        """Delete an instance from the database.

        """
        with self.session_scope() as session:
            session.delete(self)

    def _asDict(self) -> Dict[str, Any]:
        """Return a ``dict`` representation of the instance.

        """
        return {k: v for (k, v) in vars(self).items() if not
                k.startswith('_')}

    def dump(self) -> str:
        """Return a json serialized string of the instance.

        Any methods that are wrapped with ``to_json`` decorator
        will be called on the values before returning the json
        string.

        .. see-also::

            :class:`decorators.to_json`

        """
        vals = self._asDict()
        jfuncs = (getattr(self, f) for f in dir(self)
                  if hasattr(getattr(self, f), '_to_json'))

        for fn in jfuncs:
            for key in fn._keys:
                if key in vals:
                    vals[key] = fn(vals[key])

        return json.dumps(vals)

    @classmethod
    @contextlib.contextmanager
    def session_scope(cls):
        """A context manager for a session. Which creates a session
        from the import :meth:`session_maker`` method that should
        be declared by sub-class.  And is used in the database methods
        for a class/instance.

        The session will automatically try to commit any changes, rolling back
        on any errors, and finally closing the session.

        """
        if not issubclass(cls, BaseMixinABC):
            raise TypeError('Must declare a session maker method.')

        session = cls.session_maker()
        try:
            yield session
            session.commit()
        except Exception as err:
            session.rollback()
            logger.debug('error commiting: {}'.format(err))
            raise
        finally:
            session.close()

    def __str__(self) -> str:
        return self.dump()

    def __repr__(self) -> str:
        rv = "{}(".format(self.__class__.__name__)
        for key in (k for k in vars(self).keys() if not k.startswith('_')):
            rv += "{}={}, ".format(key, _quote_if_str(getattr(self, key, None)))
        return rv[:-2] + ')'
