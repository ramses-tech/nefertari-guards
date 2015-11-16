"""
CLI to manage db-ACLs:

$ nefertari-guards.count_ace
  --ace='{"action":"<action>","permission:"<permission>","principal":"<principal>"}'
-> returns count of objects with matching ACE, listed by type

$ nefertari-guards.update_ace
  --from_ace='{"action":"<action>","permission:"<permission>","principal":"<principal>"}'
  --to_ace='{"action":"<action>","permission:"<permission>","principal":"<principal>"}'
  --types=<list_of_document_types>
-> updates all objects one ACE at a time, option to restrict type(s)

API will be almost identical, e.g. nefertari_guards.count_ace(ace={...})
"""
from collections import defaultdict

from nefertari import engine
from nefertari.elasticsearch import ES


def count_ace(ace, types=None):
    """ Count number of given types documents with given ace.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param ace: Stringified ACL entry (ACE).
    :param types: List of document classes objects of which should
        be found and counted.
    :returns: Number of matching documents.
    """
    return find_by_ace(ace, types, count=True)


def update_ace(from_ace, to_ace, types=None):
    """ Update documents that contain ``from_ace`` with ``to_ace``.
    ``from_ace`` is replaced with ``to_ace`` in matching documents.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param from_ace: Stringified ACL entry (ACE) to match agains.
    :param to_ace: Stringified ACL entry (ACE) ``from_ace`` should be
        replaced with.
    :param types: List of document classes objects of which should
        be found and updated.
    """
    documents = find_by_ace(from_ace, types)
    documents = _group_by_type(documents)
    document_ids = _extract_ids(documents)
    for model, doc_ids in document_ids.items():
        _update_docs_ace(model, doc_ids, from_ace, to_ace)


def find_by_ace(ace, types=None, count=False):
    """ Find documents of types that include ace.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param ace: Stringified ACL entry (ACE) to match agains.
    :param types: List of document classes objects of which should
        be found.
    :param count: Boolean. When True objects count is returned.
    :returns: Number of matching documents when count=True or documents
        otherwise.
    """
    if types is None:
        types = list(engine.get_document_classes().values())
    es_types = _get_es_types(types)

    params = {'body': _get_es_body(ace)}
    if count:
        params['_count'] = True

    return ES(es_types).get_collection(**params)


def _get_es_types(types):
    """ Get ES types from document classes.

    :param types: List of document classes.
    :returns: String with ES type names joing by comma.
    """
    type_names = [t.__name__ for t in types
                  if getattr(t, '_index_enabled', False)]
    es_types = [ES.src2type(name) for name in type_names]
    return ','.join(es_types)


def _get_es_body(ace):
    """ Get ES body from ACE.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param ace: Stringified ACL entry (ACE) to generate body for.
    :returns: ES request body as a dict with root key "query".
    """
    must = [
        {'term': {'_acl.action': ace['action']}},
        {'term': {'_acl.principal': ace['principal']}},
        {'term': {'_acl.permission': ace['permission']}}
    ]
    body = {
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
    return body


def _group_by_type(documents):
    """ Group documents by document class.

    :param documents: List of documents to group.
    :returns: Dict of grouped documents of format
        {Model: [doc1, doc2, ...]}.
    """
    doc_classes = {}
    grouped = defaultdict(list)

    for doc in documents:
        if doc._type not in doc_classes:
            doc_classes[doc._type] = engine.get_document_cls(doc._type)
        doc_cls = doc_classes[doc._type]
        grouped[doc_cls].append(doc)

    return grouped


def _extract_ids(documents):
    """ Extract IDs from documents.

    :param documents: Dict of documents grouped by ``_group_by_type``.
    :returns: Dict of the same format with documents replaced by
        their ids.
    """
    document_ids = {}
    for model, documents in documents.items():
        pk_field = model.pk_field()
        document_ids[model] = [
            getattr(doc, pk_field) for doc in documents]
    return document_ids


def _update_docs_ace(model, doc_ids, from_ace, to_ace):
    pass
