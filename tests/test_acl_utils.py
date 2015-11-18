import pytest
from mock import patch, Mock, call

from nefertari_guards import acl_utils


class TestAclUtils(object):

    @patch('nefertari_guards.acl_utils.engine')
    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_count_ace_with_models(self, mock_find, mock_eng):
        result = acl_utils.count_ace(1, [2, 3])
        mock_find.assert_has_calls([
            call(1, [2], count=True),
            call(1, [3], count=True)])
        assert not mock_eng.get_document_classes.called
        assert result == {2: mock_find(), 3: mock_find()}

    @patch('nefertari_guards.acl_utils.engine')
    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_count_ace_without_models(self, mock_find, mock_eng):
        mock_eng.get_document_classes.return_value = {'zoo': 2}
        acl_utils.count_ace(1)
        mock_find.assert_called_with(1, [2], count=True)

    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_count_ace_valueerror(self, mock_find):
        mock_find.side_effect = ValueError
        result = acl_utils.count_ace(1, [2])
        assert result == {2: None}

    @patch('nefertari_guards.acl_utils.ES')
    @patch('nefertari_guards.acl_utils._get_es_body')
    @patch('nefertari_guards.acl_utils._get_es_types')
    def test_find_by_ace(self, mock_types, mock_body, mock_es):
        mock_types.return_value = 'Foo,Bar'
        mock_body.return_value = {'username': 'admin'}
        result = acl_utils.find_by_ace(1, 2, True)
        mock_types.assert_called_once_with(2)
        mock_body.assert_called_once_with(1)
        mock_es.assert_called_once_with('Foo,Bar')
        mock_es().get_collection.assert_called_once_with(
            _count=True, body={'username': 'admin'})
        assert result == mock_es().get_collection()

    @patch('nefertari_guards.acl_utils._get_es_types')
    def test_find_by_ace_not_es(self, mock_types):
        mock_types.return_value = []
        with pytest.raises(ValueError) as ex:
            assert acl_utils.find_by_ace({}, 1)
        assert 'No es-based models passed' in str(ex.value)

    @patch('nefertari_guards.acl_utils.ES')
    def test_get_es_types(self, mock_es):
        mock_es.src2type.side_effect = lambda x: x.lower()
        User = Mock(__name__='User', _index_enabled=False)
        Story = Mock(__name__='Story', _index_enabled=True)
        Profile = Mock(__name__='Profile', _index_enabled=True)
        types = acl_utils._get_es_types([User, Story, Profile])
        assert types == 'story,profile'
        mock_es.src2type.assert_has_calls([
            call('Profile'), call('Story'),
        ], any_order=True)

    def test_get_es_body(self):
        body = acl_utils._get_es_body({
            'action': 'allow',
            'principal': 'user12',
            'permission': 'view'
        })
        must = [
            {'term': {'_acl.action': 'allow'}},
            {'term': {'_acl.principal': 'user12'}},
            {'term': {'_acl.permission': 'view'}}
        ]
        assert body == {
            'query': {
                'filtered': {
                    'filter': {
                        'nested': {
                            'filter': {
                                'bool': {
                                    'must': must
                                }
                            },
                            'path': '_acl'
                        }
                    }
                }
            }
        }

    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_update_ace_invalid_ace(self, mock_find):
        with pytest.raises(ValueError) as ex:
            acl_utils.update_ace({}, {"action": "foo"}, 1)
        assert 'Invalid ACL action value: foo' in str(ex.value)

    @patch('nefertari_guards.acl_utils._replace_docs_ace')
    @patch('nefertari_guards.acl_utils._extract_ids')
    @patch('nefertari_guards.acl_utils._group_by_type')
    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_update_ace(self, mock_find, mock_group, mock_extr, mock_upd):
        to_ace = {
            "action": "allow",
            "principal": "a",
            "permission": "view"}
        Model = Mock()
        Model.get_by_ids.return_value = [4, 5, 6]
        mock_extr.return_value = {Model: [1, 2, 3]}
        acl_utils.update_ace({'z': 1}, to_ace, 'Z')
        mock_find.assert_called_once_with({'z': 1}, 'Z')
        mock_group.assert_called_once_with(mock_find(), 'Z')
        mock_extr.assert_called_once_with(mock_group())
        mock_upd.assert_called_once_with(
            [4, 5, 6], {'z': 1}, to_ace)
        Model.get_by_ids.assert_called_once_with([1, 2, 3])

    @patch('nefertari_guards.acl_utils.engine')
    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_update_ace_end_to_end(self, mock_find, mock_eng):
        mock_find.return_value = [Mock(username='user12', _type='User')]
        db_obj = Mock(_acl=[{'foo': 1}])
        User = Mock()
        User.pk_field.return_value = 'username'
        User.get_by_ids.return_value = [db_obj]
        mock_eng.get_document_cls.return_value = User
        to_ace = {
            "action": "allow",
            "principal": "user12",
            "permission": "view"}
        acl_utils.update_ace({'foo': 1}, to_ace)
        db_obj.update.assert_called_once_with({
            '_acl': [to_ace]})

    @patch('nefertari_guards.acl_utils.engine')
    def test_group_by_type(self, mock_eng):
        doc1 = Mock(_type='Foo')
        doc2 = Mock(_type='Bar')
        doc3 = Mock(_type='Foo')
        mock_eng.get_document_cls.side_effect = lambda x: x
        grouped = acl_utils._group_by_type([doc1, doc2, doc3])
        mock_eng.get_document_cls.assert_has_calls([
            call('Foo'), call('Bar')])
        assert mock_eng.get_document_cls.call_count == 2
        assert set(grouped.keys()) == {'Foo', 'Bar'}
        assert set(grouped['Foo']) == {doc1, doc3}
        assert set(grouped['Bar']) == {doc2}

    @patch('nefertari_guards.acl_utils.engine')
    def test_group_by_type_models_passed(self, mock_eng):
        doc1 = Mock(_type='Foo')
        doc2 = Mock(_type='Bar')
        FooModel = Mock(__name__='Foo')
        BarModel = Mock(__name__='Bar')
        grouped = acl_utils._group_by_type(
            [doc1, doc2], [FooModel, BarModel])
        assert not mock_eng.get_document_cls.called
        assert set(grouped.keys()) == {FooModel, BarModel}
        assert set(grouped[FooModel]) == {doc1}
        assert set(grouped[BarModel]) == {doc2}

    def test_extract_ids(self):
        doc1 = Mock(username='user12')
        doc2 = Mock(username='admin')
        model = Mock()
        model.pk_field.return_value = 'username'
        documents = {model: [doc1, doc2]}
        ids = acl_utils._extract_ids(documents)
        assert set(ids.keys()) == {model}
        assert set(ids[model]) == {'user12', 'admin'}

    def test_replace_docs_ace_ace_missing(self):
        doc = Mock(_acl=[])
        acl_utils._replace_docs_ace([doc], {'foo': 1}, {'bar': 1})
        assert not doc.update.called

    def test_replace_docs_ace(self):
        doc = Mock(_acl=[{'baz': 1}, {'foo': 1}, {'bar': 1}])
        acl_utils._replace_docs_ace([doc], {'foo': 1}, {'zoo': 1})
        doc.update.assert_called_once_with(
            {'_acl': [{'baz': 1}, {'zoo': 1}, {'bar': 1}]})

    def test_replace_docs_ace_duplicate_aces(self):
        doc = Mock(_acl=[{'foo': 1}, {'foo': 1}])
        acl_utils._replace_docs_ace([doc], {'foo': 1}, {'foo': 2})
        doc.update.assert_called_once_with(
            {'_acl': [{'foo': 2}, {'foo': 2}]})
