import pytest
from connexion_sql_utils import get, post, get_id, put, delete
from connexion_sql_utils.crud import _del_nulls, _parse_id

from .conftest import Foo
import json
import uuid


class Invalid(object):
    pass


def test_ensure_asset_decorator():
    with pytest.raises(TypeError):
        get(Invalid, limit=1)


def test_del_nulls():
    vals = {'data': 'not null', 'other': None, 'another': 'null'}
    assert _del_nulls(vals) == {'data': 'not null'}


def test_parse_id():
    data = {'foo_id': 'id_value', 'bar': 'baz', 'something': 'else'}
    val = next(_parse_id(data))
    assert val == 'foo_id'
    assert len(list(_parse_id(data))) == 1

    not_ids = list(_parse_id(data, _not=True))
    assert len(not_ids) == 2
    assert 'bar' in not_ids
    assert 'something' in not_ids


def test_post():
    foo, code = post(Foo, foo={'bar': 'baz'})
    assert code == 201
    foo = json.loads(foo)
    assert foo['bar'] == 'baz'
    assert 'id' in foo


def test_post_fails_with_no_kwargs():
    with pytest.raises(TypeError):
        post(Foo, **{})


def test_post_returns_400_with_invalid_data():
    _, code = post(Foo, foo={'bar': {}})
    assert code == 400


def test_get():
    assert len(get(Foo, limit=100)) >= 10
    assert len(get(Foo, limit=5)) == 5
    assert len(get(Foo, limit=0)) == 0
    assert len(get(Foo, limit=None)) >= 10


def test_id_get():
    foos = [json.loads(f) for f in get(Foo, limit=5)]
    for f in foos:
        assert json.loads(get_id(Foo, foo_id=f['id']))['id'] == f['id']

    _, code = get_id(Foo, foo_id=str(uuid.uuid4()))
    assert code == 404

    # invalid id key
    with pytest.raises(TypeError):
        get_id(Foo, foo=str(uuid.uuid4()))


def test_put():
    foo = json.loads(next(iter(get(Foo, limit=1))))
    bar = foo['bar']
    assert bar != 'bang'
    foo['bar'] = 'bang'
    updated = put(Foo, foo_id=foo['id'], foo=foo)
    updated = json.loads(updated)
    assert updated['bar'] == 'bang'
    assert updated['id'] == foo['id']


def test_put_fails_with_invalid_id_key():

    with pytest.raises(TypeError):
        put(Foo, foo={})


def test_put_fails_with_no_data_key_found():
    with pytest.raises(TypeError):
        put(Foo, foo_id=None)


def test_put_returns_400_with_bad_input_data():
    foo = json.loads(next(iter(get(Foo, limit=1))))
    foo['bar'] = {}
    _, code = put(Foo, foo_id=foo['id'], foo=foo)
    assert code == 400


def test_put_returns_404_with_invalid_id():
    _, code = put(Foo, foo_id=str(uuid.uuid4()), foo={})
    assert code == 404


def test_delete():
    foo = json.loads(next(iter(get(Foo, limit=1))))
    _, code = delete(Foo, foo_id=foo['id'])
    assert code == 204


def test_delete_returns_404_with_invalid_id():
    _, code = delete(Foo, foo_id=str(uuid.uuid4()))
    assert code == 404


def test_delete_fails_with_invalid_id_key():
    with pytest.raises(TypeError):
        delete(Foo, foo=str(uuid.uuid4()))
