from mock import patch, Mock, call

from nefertari_guards import acl_utils


class TestAclUtils(object):

    @patch('nefertari_guards.acl_utils.find_by_ace')
    def test_count_ace(self, mock_find):
        acl_utils.count_ace(1, 2)
        mock_find.assert_called_once_with(1, 2, count=True)
        acl_utils.count_ace(1)
        mock_find.assert_called_with(1, None, count=True)

    @patch('nefertari_guards.acl_utils.ES')
    @patch('nefertari_guards.acl_utils._get_es_body')
    @patch('nefertari_guards.acl_utils._get_es_types')
    def test_find_by_ace_with_types(self, mock_types, mock_body, mock_es):
        mock_types.return_value = 'Foo,Bar'
        mock_body.return_value = {'username': 'admin'}
        result = acl_utils.find_by_ace(1, 2, True)
        mock_types.assert_called_once_with(2)
        mock_body.assert_called_once_with(1)
        mock_es.assert_called_once_with('Foo,Bar')
        mock_es().get_collection.assert_called_once_with(
            _count=True, body={'username': 'admin'})
        assert result == mock_es().get_collection()

    @patch('nefertari_guards.acl_utils.ES')
    @patch('nefertari_guards.acl_utils.engine')
    @patch('nefertari_guards.acl_utils._get_es_body')
    @patch('nefertari_guards.acl_utils._get_es_types')
    def test_find_by_ace_no_types(
            self, mock_types, mock_body, mock_eng, mock_es):
        mock_eng.get_document_classes.return_value = {'model': 'model1'}
        mock_types.return_value = 'Foo,Bar'
        mock_body.return_value = {'username': 'admin'}
        result = acl_utils.find_by_ace(1)
        mock_types.assert_called_once_with(['model1'])
        mock_body.assert_called_once_with(1)
        mock_es.assert_called_once_with('Foo,Bar')
        mock_es().get_collection.assert_called_once_with(
            body={'username': 'admin'})
        mock_eng.get_document_classes.assert_called_once_with()
        assert result == mock_es().get_collection()

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
