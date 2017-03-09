# -*- coding: utf-8 -*-
"""
decorators.py
~~~~~~~~~~~~~

This module holds decorators either used by this package or for use
when creating ``sqlalchemy`` database models.

"""
from functools import wraps

from .base_mixin_abc import BaseMixinABC


def event_func(*event_names):
    """Declare a function to listen/register for an event.  The wrapped
    method should have the correct signature for an ``sqlalchemy.event``.  And
    should be declared as a ``staticmethod`` on the class that is registering
    for the event.

    .. seealso::

        :meth:`connexion_sql_utils.BaseMixin.create_id` method for an example.

    :param event_name:  The event name to register the function for.
                        Example: 'before_insert'

    """
    if not len(event_names) > 0:
        raise TypeError(event_names)

    def inner(fn):
        fn._event_names = tuple(e for e in event_names if isinstance(e, str))
        fn._event_func = True

        @wraps(fn)
        def decorator(*args, **kwargs):
            return fn(*args, **kwargs)
        return decorator
    return inner


def to_json(*keys):
    """Marks a function to be called on ``key``, when converting an instance to
    json.  This allows you to do work on an item to serialize it to json.  A
    good example use is when you use the ``Numeric`` type, that returns a
    ``Decimal`` from the database, which is not json serializable, so you must
    convert it to a string, a float, or an int, before calling ``json.dumps``.


    :param keys:  The keys/attributes to call the method on when converting.

    """
    def inner(fn):
        fn._keys = keys
        fn._to_json = True

        @wraps(fn)
        def decorator(*args, **kwargs):
            return fn(*args, **kwargs)
        return decorator
    return inner


def ensure_asset(fn):
    """Ensure's that an asset passes an ``isinstance`` or an ``issubclass``
    check for :class:`BaseMixinABC` before calling a function. The asset must
    be the first arg to the function.

    """
    @wraps(fn)
    def decorator(asset, *args, **kwargs):
        if not any((isinstance(asset, BaseMixinABC),
                    issubclass(asset, BaseMixinABC))):
            raise TypeError(asset)
        return fn(asset, *args, **kwargs)
    return decorator
