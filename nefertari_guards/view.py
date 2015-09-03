class ACLFilterViewMixin(object):
    """ Base view class that applies ACL filtering. """

    def get_collection_es(self):
        """ Override method to apply ACL filtering when authentication
        is enabled.
        """
        from nefertari_guards.elasticsearch import ACLFilterES
        params = self._query_params.copy()

        if self._auth_enabled:
            params['_principals'] = self.request.effective_principals

        return ACLFilterES(self.Model.__name__).get_collection(**params)
