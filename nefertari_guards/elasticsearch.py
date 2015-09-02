from nefertari.elasticsearch import ES
from nefertari.utils import dictset


def includeme(config):
    Settings = dictset(config.registry.settings)
    ACLFilterES.setup(Settings)


class ACLFilterES(ES):
    """ Nefertari ES subclass that applies ACL filtering when
    '_identifiers' param is passed.
    """
    def build_search_params(self, params):
        """ Override to add ACL filter params when '_identifiers'
        param is passed.
        """
        _identifiers = params.pop('_identifiers', None)
        _params = super(ACLFilterES, self).build_search_params(params)

        if _identifiers:
            permissions_query = build_acl_query(_identifiers)
            _params['body'] = {'query': {'filtered': _params['body']}}
            _params['body']['query']['filtered'].update(permissions_query)

        return _params


def _build_acl_bool_terms(acl, action_obj):
    """ Build ACL bool filter from given Pyramid ACL.

    :param acl: Valid Pyramid ACL used to build a bool filter query.
    :param action_obj: Pyramid ACL action object (Allow, Deny)
    """
    from nefertari_guards import engine
    acl = engine.ACLField.stringify_acl(acl)
    action = engine.ACLField._stringify_action(action_obj)
    identifiers = sorted(set([ace['identifier'] for ace in acl]))
    permissions = sorted(set([ace['permission'] for ace in acl]))
    return [
        {'term': {'_acl.action': action}},
        {'terms': {'_acl.identifier': identifiers}},
        {'terms': {'_acl.permission': permissions}},
    ]


def _build_acl_from_identifiers(identifiers, action_obj):
    """ Build ACL with 'all' and 'view' permissions for which
    of :identifiers: controlled by :action_obj:.

    :param identifiers: List of valid Pyramid ACL identifiers for
        which ACL should be built.
    :param action_obj: Pyramid ACL action object (Allow, Deny) which
        should be used in all ACEs of ACL.
    :return: Valid Pyramid ACL.
    """
    from pyramid.security import ALL_PERMISSIONS
    acl = []
    for ident in identifiers:
        acl += [
            (action_obj, ident, ALL_PERMISSIONS),
            (action_obj, ident, 'view'),
        ]
    return acl


def build_acl_query(identifiers):
    """ Build ES query to filter collection by only getting items
    for which user has 'view' or 'all' permission and does not have
    any of these permissions denied.

    Object is shown when its ACL allows 'all' or 'view' permissions
    to any one of identifiers and doesn't deny 'all' or 'view' permissions
    to any one of identifiers.
    Order of ACEs in ACL doesn't affect filtering results.

    :param identifiers: List of valid Pyramid ACL identifiers for
        which object permissions should be allowed.
    :return: ES 'filter' query part.
    """
    from pyramid.security import Allow, Deny

    # Generate ACLs from identifiers
    allowed_acl = _build_acl_from_identifiers(identifiers, Allow)
    denied_acl = _build_acl_from_identifiers(identifiers, Deny)

    # Generate bool terms queries
    must = _build_acl_bool_terms(allowed_acl, Allow)
    must_not = _build_acl_bool_terms(denied_acl, Deny)

    def get_bool_filter(query_terms):
        return {
            'nested': {
                'path': '_acl',
                'filter': {'bool': {'must': query_terms}}
            }
        }

    return {
        'filter': {
            'bool': {
                'must': get_bool_filter(must),
                'must_not': get_bool_filter(must_not),
            }
        }
    }
