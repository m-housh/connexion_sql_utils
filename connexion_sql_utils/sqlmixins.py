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
    dump_dict = False

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
    def query_by(cls, session=None, **kwargs):
        """Return a query statement for the class.

        :param session:  An optional sqlalchemy session, if one is not passed
                         a session will be created for the query.
        :param kwargs:  kwargs passed into the query to filter results.

        This would be simalar to::

            >>> session.query(MyDbModel).filter_by(id=1234)

        """
        if session is not None:
            return session.query(cls).filter_by(**kwargs)

        with cls.session_scope() as session:
            return session.query(cls).filter_by(**kwargs)

    @classmethod
    def get_id(cls, id, session=None):
        """Get by id.

        :param id:  The unique identifier for the class.
        :param session:  An optional sqlalchemy session, if one is not passed
                         a session will be created for the query.

        This is would be like::

            >>> session.query(MyDbModel).filter_by(id=1234).first()

        """
        try:
            return cls.query_by(id=id, session=session).first()
        except:
            return None

    def _update(self, session, kwargs):
        for key in (k for k in vars(self.__class__)
                    if not k.startswith('_')):
            if kwargs.get(key, None) is not None:
                setattr(self, key, kwargs[key])
        session.add(self)

    def update(self, session=None, **kwargs):
        """Update attributes on an instance.

        :param kwargs:  The attributes to update on the instance.  Any
                        attribute not declared on the class is ignored.
        :param session:  An optional sqlalchemy session, if one is not passed
                         a session will be created for the query.

        """
        if session is not None:
            return self._update(session, kwargs)

        with self.session_scope() as session:
            return self._update(session, kwargs)

    def save(self, session=None):
        """Save an instance to the database.

        :param session:  An optional sqlalchemy session, if one is not passed
                         a session will be created for the query.

        """
        if session is not None:
            return session.add(self)

        with self.session_scope() as session:
            return session.add(self)

    def delete(self, session=None):
        """Delete an instance from the database.

        :param session:  An optional sqlalchemy session, if one is not passed
                         a session will be created for the query.

        """
        if session is not None:
            return session.delete(self)
        with self.session_scope() as session:
            return session.delete(self)

    def _asDict(self) -> Dict[str, Any]:
        """Return a ``dict`` representation of the instance.

        """
        return {k: v for (k, v) in vars(self).items() if not
                k.startswith('_')}

    def dump(self, _dict=None) -> str:
        """Return a json serialized string or a dict representation of the
        instance.

        Any methods that are wrapped with ``to_json`` decorator
        will be called on the values before returning the json
        string.

        :param _dict:  If ``True`` return a dict instead of a json string,
                       or the class attribute ``dump_dict`` is true on a
                       sub-class.

        .. see-also::

            :class:`decorators.to_json`

        """
        dump_dict = _dict or self.dump_dict
        vals = self._asDict()
        to_json_funcs = (getattr(self, f) for f in dir(self)
                         if hasattr(getattr(self, f), '_to_json'))

        for fn in to_json_funcs:
            for key in fn._keys:
                if key in vals:
                    vals[key] = fn(vals[key])

        dump_funcs = (getattr(self, f) for f in dir(self)
                      if hasattr(getattr(self, f), '_dump_method'))

        for fn in dump_funcs:
            vals = fn(vals)

        return vals if dump_dict is True else json.dumps(vals)

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
