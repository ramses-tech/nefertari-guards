from nefertari.elasticsearch import ES, _ESDocs
from nefertari.utils import dictset, DataProxy, is_document
from nefertari.resource import PERMISSIONS

from nefertari_guards import engine


def includeme(config):
    Settings = dictset(config.registry.settings)
    ACLFilterES.setup(Settings)


class ACLFilterES(ES):
    """ Nefertari ES subclass that applies ACL filtering when
    'request' param is passed and auth is enabled.
    """
    def build_search_params(self, params):
        """ Overriden to add ACL filter params when '_principals'
        param is passed.

        :param params: ES query params
        :return: ES query params
        """
        _principals = params.pop('_principals', None)
        _params = super(ACLFilterES, self).build_search_params(params)

        if _principals:
            old_body = _params['body']
            permissions_query = build_acl_query(
                _principals, self._req_permission)
            if 'query' in old_body:
                permissions_query['must'].append(old_body['query'])
            _params['body'] = {'query': {'bool': permissions_query}}
        return _params

    def aggregate(self, request=None, **params):
        """ Overriden to support ACL filtering. """
        if auth_enabled(request):
            self._req_permission = PERMISSIONS[request.action]
            params['_principals'] = request.effective_principals
        return super(ACLFilterES, self).aggregate(**params)

    def get_collection(self, request=None, **params):
        """ Overriden to support ACL filtering.

        When auth is enabled, adds '_principals' param to perform ACL
        filtering during query and performs ACL filtering of results'
        relationships.

        :param request: Pyramid Request instance that represents current
            request
        :return: Found and ACL filtered (if auth enabled) documents
            wrapped in DataProxy
        """
        _auth_enabled = auth_enabled(request)
        if _auth_enabled:
            self._req_permission = PERMISSIONS[request.action]
            params['_principals'] = request.effective_principals
        documents = super(ACLFilterES, self).get_collection(**params)

        if _auth_enabled and isinstance(documents, _ESDocs):
            _nefertari_meta = documents._nefertari_meta
            documents = _ESDocs([
                check_relations_permissions(request, doc)
                for doc in documents])
            documents._nefertari_meta = _nefertari_meta

        return documents

    def get_item(self, request=None, **kw):
        """ Overriden to support ACL filtering.

        When auth is enabled, performs ACL filtering of found document's
        relationships.

        :param request: Pyramid Request instance that represents current
            request
        :return: Found ES document wrapped in DataProxy
        """
        document = super(ACLFilterES, self).get_item(**kw)

        if auth_enabled(request):
            return check_relations_permissions(request, document)

        return document


def auth_enabled(request):
    return (
        request is not None and
        dictset(request.registry.settings).asbool('auth'))


def check_relations_permissions(request, document):
    """ Check permissions of document relationships.

    If related document can not be visible by user, it is replaced with
    None or removed from collection display. Each related document
    permissions are checked with `_check_permissions` function.

    :param request: Pyramid Request instance that represents current
        request
    :param document: Either DataProxy instance or dictionary containing
        ES document data
    :return: Document of the same type as input one but with ACL-filtered
        relationships
    """
    if isinstance(document, DataProxy):
        data = document._data
    else:
        data = document

    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            checked = [_check_permissions(request, val) for val in value]
            checked = [val for val in checked if val is not None]
        else:
            checked = _check_permissions(request, value)
        data[key] = checked
    return document


class SimpleContext(object):
    """ Simple context class used in _check_permissions. """
    def __init__(self, acl):
        self.__acl__ = acl


def _check_permissions(request, document):
    """ Check permissions of ES document.

    :param request: Pyramid Request instance that represents current
        request
    :param document: Dict representing valid ES document
    :return: Input document if it's not a valid document. None if user
        doesn't have permissions to see the document. Document with
        filtered relationships if user has permissions to see it.
    """
    # Make sure `document` is a valid ES document
    if not is_document(document):
        return document

    # Check whether document can be displayed to user
    acl = engine.ACLField.objectify_acl(document.get('_acl', []))
    context = SimpleContext(acl)
    if request.has_permission('view', context):
        return check_relations_permissions(request, document)


def _build_acl_bool_terms(acl, action_obj):
    """ Build ACL bool filter from given Pyramid ACL.

    :param acl: Valid Pyramid ACL used to build a bool filter query.
    :param action_obj: Pyramid ACL action object (Allow, Deny)
    """
    acl = engine.ACLField.stringify_acl(acl)
    action = engine.ACLField._stringify_action(action_obj)
    principals = sorted(set([ace['principal'] for ace in acl]))
    permissions = sorted(set([ace['permission'] for ace in acl]))
    return [
        {'term': {'_acl.action': action}},
        {'terms': {'_acl.principal': principals}},
        {'terms': {'_acl.permission': permissions}},
    ]


def _build_acl_from_principals(principals, action_obj, req_permission):
    """ Build ACL with 'all' and `req_permission` permissions for which
    of :principals: controlled by :action_obj:.

    :param principals: List of valid Pyramid ACL principals for
        which ACL should be built.
    :param action_obj: Pyramid ACL action object (Allow, Deny) which
        should be used in all ACEs of ACL.
    :param req_permission: Requested permission which is used to
        perform ACL filtering.
    :return: Valid Pyramid ACL.
    """
    from pyramid.security import ALL_PERMISSIONS
    acl = []
    for ident in principals:
        acl += [
            (action_obj, ident, ALL_PERMISSIONS),
            (action_obj, ident, req_permission),
        ]
    return acl


def build_acl_query(principals, req_permission):
    """ Build ES query to filter collection by only getting items
    for which user has `req_permission` or 'all' permission and does
    not have any of these permissions denied.

    Object is shown when its ACL allows 'all' or 'req_permission'
    permissions to any one of principals and doesn't deny 'all' or
    'req_permission' permissions to any one of principals.
    Order of ACEs in ACL doesn't affect filtering results.

    :param principals: List of valid Pyramid ACL principals for
        which object permissions should be allowed.
    :param req_permission: Requested permission which is used to
        perform ACL filtering.
    :return: ES 'filter' query part.
    """
    from pyramid.security import Allow, Deny

    # Generate ACLs from principals
    allowed_acl = _build_acl_from_principals(
        principals, Allow, req_permission)
    denied_acl = _build_acl_from_principals(
        principals, Deny, req_permission)

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
        'must': [get_bool_filter(must)],
        'must_not': get_bool_filter(must_not),
    }


def get_es_item_acl(item):
    """ Get item ACL and return objectified version or it. """
    acl = getattr(item, '_acl', ())
    return engine.ACLField.objectify_acl([
        ace._data for ace in acl])
