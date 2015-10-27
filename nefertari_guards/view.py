from nefertari.view_helpers import ESAggregator

from nefertari_guards.elasticsearch import ACLFilterES


class ACLESAggregator(ESAggregator):
    """ Aggregator that applies ACL filtering when auth is enabled. """

    def aggregate(self):
        """ Perform aggregation and return response. """
        aggregations_params = self.pop_aggregations_params()
        if self.view._auth_enabled:
            self.check_aggregations_privacy(aggregations_params)
        self.stub_wrappers()

        params = self._query_params.copy()
        params['_aggregations_params'] = aggregations_params

        return ACLFilterES(self.view.Model.__name__).aggregate(
            request=self.view.request, **params)


class ACLFilterViewMixin(object):
    """ Base view class that applies ACL filtering. """

    def get_collection_es(self):
        """ Override method to use ACLFilterES and pass request to it. """
        params = self._query_params.copy()
        return ACLFilterES(self.Model.__name__).get_collection(
            request=self.request, **params)

    def _setup_aggregation(self, aggregator=None, **kwargs):
        """ Override to use ACLESAggregator. """
        return super(ACLFilterViewMixin, self)._setup_aggregation(
            aggregator=ACLESAggregator, **kwargs)
