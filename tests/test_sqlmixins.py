
import pytest

from sqlalchemy.orm import Session
from connexion_sql_utils import BaseMixin, BaseMixinABC, get, event_func, \
    to_json
from .conftest import Foo

import json


def test_save():
    foo = Foo(bar='some data')
    foo.save()
    assert Foo.query_by(bar='some data').first() is not None

    foo.id = 'bad id'
    with pytest.raises(Exception):
        foo.save()


def test_save_with_session():
    foo = Foo(bar='a bar')
    with Foo.session_scope() as session:
        foo.save(session=session)
        session.commit()

    assert Foo.query_by(bar='a bar').first() is not None


def test_update():
    foo = Foo(bar='data')
    assert foo.bar == 'data'
    foo.update(bar='different data')
    assert foo.bar == 'different data'


def test_update_with_session():
    foo = Foo.query_by().first()
    old_bar = foo.bar
    new_bar = '{}-new'.format(old_bar)

    with Foo.session_scope() as session:
        foo.update(bar=new_bar, session=session)
        assert foo.bar == new_bar
        session.commit()

    # check that changes persist
    loaded = Foo.query_by(bar=new_bar).first()
    assert loaded is not None


def test_get_id():
    foo = json.loads(next(iter(get(Foo, limit=1))))
    assert foo['id'] is not None
    queried = Foo.get_id(foo['id'])
    assert queried.id == foo['id']
    assert Foo.get_id(1000) is None


def test_query_by():
    query = Foo.query_by().all()
    for q in query:
        assert isinstance(q, Foo)


def test_query_by_with_session():
    with Foo.session_scope() as session:
        query = Foo.query_by(session=session).all()

        for q in query:
            assert isinstance(q, Foo)


def test_event_func_fails_with_no_event_name():

    with pytest.raises(TypeError):
        @event_func()
        def oops():
            pass


def test_quote_if_string():
    foo = Foo(bar='something')
    assert "'something'" in repr(foo)
    foo = Foo(bar=1)
    assert str(1) in repr(foo)


def test_to_json_funcs():
    class JSON(BaseMixin):

        def __init__(self, data=None, other=None):
            self.data = data
            self.other = other

        @to_json('data', 'other')
        def hello_world(self, val):
            return 'hello world'

    j = JSON(data='data', other='other')
    assert j.data == 'data'
    assert j.other == 'other'

    jl = json.loads(j.dump())
    assert jl['data'] == 'hello world'
    assert jl['other'] == 'hello world'


def test_session_scope():
    with Foo.session_scope() as s:
        assert isinstance(s, Session)
        foo = Foo(bar='custom data')
        s.add(foo)

    saved = Foo.query_by(bar='custom data')
    assert saved is not None

    with pytest.raises(Exception):
        with Foo.session_scope() as s:
            foo = s.query(Foo).first()
            foo.id = 'invalid'
            s.add(foo)
            s.commit()


def test_dump():
    foo = Foo(bar='data')
    # baz is added with the dump_method decorator.
    dumped = foo.dump()
    assert isinstance(dumped, str)
    assert json.loads(foo.dump()) == {"bar": "data", "baz": "bang"}
    assert json.loads(str(foo)) == {"bar": "data", "baz": "bang"}

    dumped = foo.dump(_dict=True)
    assert isinstance(dumped, dict)
    assert dumped == {"bar": "data", "baz": "bang"}


def test_delete():
    foo = Foo(bar='my data')
    foo.save()
    assert foo.id is not None
    id = foo.id
    foo.delete()
    with Foo.session_scope() as s:
        q = s.query(Foo).filter(Foo.id == id).first()
        assert q is None


def test_delete_with_session():
    foo = Foo(bar='delete-ses')
    foo.save()

    with Foo.session_scope() as session:
        foo.delete(session=session)
        session.commit()

    # check delete persists
    assert Foo.query_by(bar='delete-ses').first() is None


def test_session_scope_fails_with_invalid_subclass():

    class Invalid(BaseMixin):
        pass

    assert not issubclass(Invalid, BaseMixinABC)

    with pytest.raises(TypeError):
        with Invalid.session_scope():
            pass


def test_dump_method():
    foo = Foo.query_by().first()

    loaded = json.loads(foo.dump())
    assert 'baz' in loaded
    assert loaded['baz'] == 'bang'
