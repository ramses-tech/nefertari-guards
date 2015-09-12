from mock import Mock

from nefertari_guards import documents as docs


class TestDocumentACLMixin(object):

    def _mocked_document_cls(self):
        engine = Mock()
        document_cls = docs.get_document_mixin(engine)
        document_cls._engine_mock = engine
        document_cls.pk_field = Mock(return_value='id')
        document_cls.id = 1
        return document_cls

    def test_default_item_acl(self):
        document_cls = self._mocked_document_cls()
        document_cls.__item_acl__ = 'foo'
        assert document_cls.default_item_acl() == 'foo'

    def test_get_acl(self):
        document_cls = self._mocked_document_cls()
        document = document_cls()
        document._acl = 'foo'
        result = document.get_acl()
        field = document_cls._engine_mock.ACLField
        field.objectify_acl.assert_called_once_with('foo')
        assert result == field.objectify_acl()

    def test_set_default_acl(self):
        document_cls = self._mocked_document_cls()
        document_cls.__item_acl__ = 'foo'
        document = document_cls()
        document._is_created = Mock(return_value=True)
        document._acl = None
        document._set_default_acl()
        field = document_cls._engine_mock.ACLField
        field.stringify_acl.assert_called_once_with('foo')
        assert document._acl == field.stringify_acl()

    def test_set_default_acl_not_created(self):
        document_cls = self._mocked_document_cls()
        document_cls.__item_acl__ = 'foo'
        document = document_cls()
        document._is_created = Mock(return_value=False)
        document._acl = None
        document._set_default_acl()
        assert document._acl is None

    def test_set_default_acl_already_set(self):
        document_cls = self._mocked_document_cls()
        document_cls.__item_acl__ = 'foo'
        document = document_cls()
        document._is_created = Mock(return_value=True)
        document._acl = 123
        document._set_default_acl()
        assert document._acl == 123
