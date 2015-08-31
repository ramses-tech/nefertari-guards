class ACLFilterViewMixin(object):
    """ Base view class that applies ACL filtering. """

    def get_collection_es(self):
        """ Override method to apply ACL filtering when authentication
        is enabled.
        """
        from nefertari.elasticsearch import ES
        params = self._query_params.copy()

        if self._auth_enabled:
            params['_identifiers'] = self.request.effective_principals

        return ES(self.Model.__name__).get_collection(**params)
