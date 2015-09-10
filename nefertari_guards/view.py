from nefertari_guards.elasticsearch import ACLFilterES


class ACLFilterViewMixin(object):
    """ Base view class that applies ACL filtering. """

    def get_collection_es(self):
        """ Override method to use ACLFilterES and pass request to it. """
        params = self._query_params.copy()
        return ACLFilterES(self.Model.__name__).get_collection(
            request=self.request, **params)
