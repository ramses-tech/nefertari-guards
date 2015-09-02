from mock import patch, call
from nefertari_guards import elasticsearch as es

from .fixtures import engine_mock


class TestESHelpers(object):

    def test_build_acl_bool_terms(self, engine_mock):
        from pyramid.security import Allow
        engine_mock.ACLField.stringify_acl.return_value = [
            {'identifier': 'user', 'permission': 'view'},
            {'identifier': 'admin', 'permission': 'create'},
            {'identifier': 'admin', 'permission': 'view'},
        ]
        engine_mock.ACLField._stringify_action.return_value = 'allow'
        terms = es._build_acl_bool_terms('zoo', Allow)
        engine_mock.ACLField.stringify_acl.assert_called_once_with('zoo')
        engine_mock.ACLField._stringify_action.assert_called_once_with(Allow)
        assert len(terms) == 3
        assert {'term': {'_acl.action': 'allow'}} in terms
        assert {'terms': {'_acl.identifier': ['admin', 'user']}} in terms
        assert {'terms': {'_acl.permission': ['create', 'view']}} in terms

    def test_build_acl_from_identifiers(self):
        from pyramid.security import Deny, ALL_PERMISSIONS
        acl = es._build_acl_from_identifiers(['admin', 'user'], Deny)
        assert (Deny, 'user', 'view') in acl
        assert (Deny, 'user', ALL_PERMISSIONS) in acl
        assert (Deny, 'admin', 'view') in acl
        assert (Deny, 'admin', ALL_PERMISSIONS) in acl

    @patch('nefertari_guards.elasticsearch._build_acl_bool_terms')
    @patch('nefertari_guards.elasticsearch._build_acl_from_identifiers')
    def test_build_acl_query(self, build_ids, build_terms):
        from pyramid.security import Deny, Allow
        build_ids.return_value = [(1, 2, 3)]
        build_terms.return_value = 'foo'
        query = es.build_acl_query(['user', 'admin'])
        build_ids.assert_has_calls([
            call(['user', 'admin'], Allow),
            call(['user', 'admin'], Deny),
        ])
        build_terms.assert_has_calls([
            call([(1, 2, 3)], Allow),
            call([(1, 2, 3)], Deny),
        ])
        must = must_not = {
            'nested': {
                'path': '_acl',
                'filter': {'bool': {'must': 'foo'}}
            }
        }
        assert query == {
            'filter': {
                'bool': {
                    'must': must,
                    'must_not': must_not
                }
            }
        }


class TestACLFilterES(object):

    @patch('nefertari_guards.elasticsearch.build_acl_query')
    def test_build_search_params(self, mock_build):
        obj = es.ACLFilterES('Foo', 'foondex', chunk_size=10)
        mock_build.return_value = {'filter': 'zoo'}
        params = obj.build_search_params(
            {'foo': 1, '_limit': 10, '_identifiers': [3, 4]})
        assert sorted(params.keys()) == sorted([
            'body', 'doc_type', 'from_', 'size', 'index'])
        assert params['body'] == {
            'query': {
                'filtered': {
                    'filter': 'zoo',
                    'query': {'query_string': {'query': 'foo:1'}}
                }
            }
        }
        assert params['index'] == 'foondex'
        assert params['doc_type'] == 'Foo'
        mock_build.assert_called_once_with([3, 4])
