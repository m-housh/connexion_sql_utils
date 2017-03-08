import contextlib
from connexion_sql_utils import BaseMixinABC


class QueryBy(object):

    @classmethod
    def query_by(cls):
        pass


class GetId(object):

    @classmethod
    def get_id(cls):
        pass


class Save(object):

    def save(self):
        pass


class Update(object):

    def update(self):
        pass


class Delete(object):

    def delete(self):
        pass


class Dump(object):

    def dump(self):
        return 'hello world'


class AsDict(object):

    def _asDict(self):
        pass


class SessionScope(object):

    @staticmethod
    @contextlib.contextmanager
    def session_scope():
        yield


class SessionMaker(object):

    @classmethod
    def session_maker(cls):
        pass


class Valid(SessionScope, AsDict, Dump, Delete, Update, Save, GetId, QueryBy,
            SessionMaker, BaseMixinABC):
    pass


class ValidObject(SessionScope, AsDict, Dump, Delete, Update, Save,
                  GetId, QueryBy, SessionMaker):
    pass


def test_subclass_hook():
    assert issubclass(Valid, BaseMixinABC)
    assert isinstance(Valid(), BaseMixinABC)
    assert issubclass(ValidObject, BaseMixinABC)
    assert isinstance(ValidObject(), BaseMixinABC)
    assert not isinstance(object(), BaseMixinABC)


def test_str_calls_dump():
    assert str(Valid()) == 'hello world'
