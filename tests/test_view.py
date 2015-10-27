from mock import Mock, patch

from nefertari.view import BaseView
from nefertari_guards.view import ACLFilterViewMixin, ACLESAggregator


class TestACLFilterViewMixin(object):
    @patch('nefertari_guards.view.ACLFilterES')
    def test_get_collection_es_auth_enabled(self, mock_es):
        class View(ACLFilterViewMixin, BaseView):
            pass

        request = Mock(content_type='', method='', accept=[''])
        view = View(
            context={}, request=request,
            _query_params={'foo': 'bar'})
        view._auth_enabled = True
        view.Model = Mock(__name__='MyModel')
        view._query_params['q'] = 'movies'
        result = view.get_collection_es()
        mock_es.assert_called_once_with('MyModel')
        mock_es().get_collection.assert_called_once_with(
            q='movies', foo='bar', request=request)
        assert result == mock_es().get_collection()


class TestACLESAggregator(object):

    class DemoView(object):
        _aggregations_keys = ('test_aggregations',)
        _query_params = {}
        _json_params = {}
        request = Mock(effective_principals=['g:user'])

    @patch('nefertari_guards.view.ACLFilterES')
    def test_aggregate(self, mock_es):
        mock_es.settings = Mock(index_name='aa')
        view = self.DemoView()
        view._auth_enabled = True
        view.Model = Mock(__name__='FooBar')
        aggregator = ACLESAggregator(view)
        aggregator.check_aggregations_privacy = Mock()
        aggregator.stub_wrappers = Mock()
        aggregator.pop_aggregations_params = Mock(return_value={'foo': 1})
        aggregator._query_params = {'q': '2', 'zoo': 3}
        aggregator.aggregate()
        aggregator.stub_wrappers.assert_called_once_with()
        aggregator.pop_aggregations_params.assert_called_once_with()
        aggregator.check_aggregations_privacy.assert_called_once_with(
            {'foo': 1})
        mock_es.assert_called_once_with('FooBar')
        mock_es().aggregate.assert_called_once_with(
            _aggregations_params={'foo': 1},
            request=self.DemoView.request, q='2', zoo=3)
