# -*- coding: utf-8 -*-
"""
crud.py
~~~~~~~

This module contains methods that can be used to query the database.
They are designed to be used in conjunction with the :class:`BaseMixin` or
a class that passes a check for the :class:`BaseMixinABC` methods.

These methods do work stand-alone, however they are designed to be used
with ``functools.partial`` and ``connexion``.  ``Connexion`` expects the
functions for it's api calls to be module level functions.  So this allows
one to declare an ``sqlalchemy`` model that typically derives from the
:class:`BaseMixin`.  Then one is able to just create partial's of these
utility functions for the actual operations, providing the correct kwargs
needed by ``connexion``.

The only caveat is that any of the functions that require an ``id``, must
have 'id' in their kwarg key.


All of the functions in this module will fail if the ``asset`` does not
pass ``isinstance`` or an ``issubclass`` check for the :class:`BaseMixinABC`.
A class does not need to directly inherit from :class:`BaseMixinABC`, it just
must declare all the methods of that interface.

"""
import logging
from typing import Iterable
from connexion import NoContent

from .decorators import ensure_asset


def _del_nulls(kwargs):
    """Delete keys that are ``None`` or ``'null'`` for kwargs.

    """
    null_keys = [k for (k, v) in kwargs.items() if v is None or v is 'null']
    for k in null_keys:
        del(kwargs[k])
    return kwargs


def _parse_id(kwargs, _not=False) -> Iterable[str]:
    """Find the id key, if ``_not`` is True, return the keys that are not
    the id key.

    """
    for k in kwargs.keys():
        if _not is False and 'id' in k:
            yield k
        elif _not is True and 'id' not in k:
            yield k


@ensure_asset
def get(asset, limit=1, **kwargs):
    """Retrieves assets from the database.  Assets are always returned as a
    list(array) of size ``limit``.

    :param asset:  The database class to query. This must inherit from
                   :class:`Base`
    :param limit: The limit for the return values
    :param kwargs: Are query parameters to filter the assets by

    :raises TypeError: if the ``asset`` does not inherit from :class:`Base`

    """
    if limit is None:
        limit = 100
    kwargs = _del_nulls(kwargs)
    resp = asset.query_by(**kwargs)
    return [r.dump() for r in resp][:limit]


@ensure_asset
def get_id(asset, **kwargs):
    """Get an asset by the unique id.

    The key for the id must have 'id' in the name in the kwargs.

    Example::

        get_id(Foo, foo_id=1)  # works
        get_id(Foo, foo=1)  # TypeError

    """
    id_key = next(_parse_id(kwargs), None)
    if id_key is None:
        raise TypeError('Could not parse id key:{}'.format(kwargs))
    instance = asset.get_id(kwargs[id_key])
    if instance is not None:
        return instance.dump()
    return NoContent, 404


@ensure_asset
def post(asset, **kwargs):
    """Post an asset to the database.

    :param asset:  The database class to query. This must inherit from
                   :class:`Base`
    :param kwargs:  This should be of length 1, the key only matters to
                    ``connexion``, the value for the key is used as the
                    kwargs to make an ``asset`` instance to save to the
                    database. This allows this to be used with
                    ``functools.partial``.

    :raises TypeError: if the ``asset`` does not inherit from :class:`Base`

    """
    if not len(kwargs) > 0:
        raise TypeError('Not enough context, kwargs should be of length 1:{}'
                        .format(kwargs))

    vals = next(iter(kwargs.values()))
    instance = asset(**vals)
    try:
        instance.save()
        logging.debug('Created:{}:{}'.format(asset.__name__, repr(instance)))
        return instance.dump(), 201
    except Exception as err:
        logging.debug('Exception:post_id:{}'.format(err))
    return NoContent, 400


@ensure_asset
def put(asset, **kwargs):
    """Update an asset.  The kwargs should be of length 2, one of which is an
    id key (has 'id' in it's name), used to look up the item in the database.
    The other key should not have 'id' in it's name, and used as the data to
    update the asset.

    :param asset:  The database asset.

    :raises TypeError:  If could not find a key with 'id' in it's name or could
                        not find a key without 'id' in it's name.

    """
    id_key = next(_parse_id(kwargs), None)

    if id_key is None:
        raise TypeError('unable to parse id key')

    data_key = next(_parse_id(kwargs, _not=True), None)
    if data_key is None:
        raise TypeError('unable to parse data')

    instance = asset.get_id(kwargs[id_key])
    if instance is not None:
        try:
            instance.update(**dict(kwargs[data_key]))
            logging.debug('Updated:{}:{}'
                          .format(asset.__name__, repr(instance)))
            return instance.dump()
        except Exception as err:
            logging.debug('Failed:post:{}:{}'.format(asset.__name__, err))
            return NoContent, 400

    return NoContent, 404


@ensure_asset
def delete(asset, **kwargs):
    """Delete an asset

    """
    id_key = next(_parse_id(kwargs), None)
    if id_key is None:
        raise TypeError(id_key)

    instance = asset.get_id(kwargs[id_key])
    if instance is not None:
        instance.delete()
        logging.debug('Deleting asset:{}:{}'
                      .format(asset.__name__, repr(instance)))
        return NoContent, 204
    return NoContent, 404
