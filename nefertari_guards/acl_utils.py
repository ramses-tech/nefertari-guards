"""
CLI to manage db-ACLs:

$ nefertari-guards.count_ace
  --ace='{"action":"<action>","permission:"<permission>","principal":"<principal>"}'
  --models=<list_of_document_models>
-> returns count of objects with matching ACE, listed by type

$ nefertari-guards.update_ace
  --from_ace='{"action":"<action>","permission:"<permission>","principal":"<principal>"}'
  --to_ace='{"action":"<action>","permission:"<permission>","principal":"<principal>"}'
  --models=<list_of_document_models>
-> updates all objects one ACE at a time, option to restrict type(s)

API will be almost identical, e.g. nefertari_guards.count_ace(ace={...})
"""
import logging
from collections import defaultdict
from copy import deepcopy

from nefertari import engine
from nefertari.elasticsearch import ES

from .base import ACLEncoderMixin


log = logging.getLogger(__name__)


def count_ace(ace, models=None):
    """ Count number of given models items with given ace.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param ace: Stringified ACL entry (ACE).
    :param models: List of document classes objects of which should
        be found and counted.
    :returns: Number of matching documents.
    """
    if models is None:
        models = list(engine.get_document_classes().values())
    return find_by_ace(ace, models, count=True)


def update_ace(from_ace, to_ace, models=None):
    """ Update documents that contain ``from_ace`` with ``to_ace``.
    In fact ``from_ace`` is replaced with ``to_ace`` in matching
    documents.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param from_ace: Stringified ACL entry (ACE) to match agains.
    :param to_ace: Stringified ACL entry (ACE) ``from_ace`` should be
        replaced with. Value is validated.
    :param models: List of document classes objects of which should
        be found and updated.
    """
    if models is None:
        models = list(engine.get_document_classes().values())
    ACLEncoderMixin().validate_acl([to_ace])
    documents = find_by_ace(from_ace, models)
    documents = _group_by_type(documents, models)
    document_ids = _extract_ids(documents)
    for model, doc_ids in document_ids.items():
        items = model.get_by_ids(doc_ids)
        _replace_docs_ace(items, from_ace, to_ace)


def find_by_ace(ace, models, count=False):
    """ Find documents of models that include ace.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param ace: Stringified ACL entry (ACE) to match agains.
    :param models: List of document classes objects of which should
        be found.
    :param count: Boolean. When True objects count is returned.
    :returns: Number of matching documents when count=True or documents
        otherwise.
    """
    es_types = _get_es_types(models)

    params = {'body': _get_es_body(ace)}
    if count:
        params['_count'] = True

    documents = ES(es_types).get_collection(**params)
    docs_count = (documents if isinstance(documents, int)
                  else len(documents))
    log.debug('Found {} documents that match ACE {}.'.format(
        docs_count, str(ace)))
    return documents


def _get_es_types(models):
    """ Get ES types from document model classes.

    :param models: List of document classes.
    :returns: String with ES type names joing by comma.
    """
    type_names = [t.__name__ for t in models
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


def _group_by_type(documents, models=None):
    """ Group documents by document class.

    :param documents: List of documents to group.
    :param models: List models classes of documents.
    :returns: Dict of grouped documents of format
        {Model: [doc1, doc2, ...]}.
    """
    doc_classes = {}
    if models is not None:
        doc_classes.update({model.__name__: model for model in models})

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


def _replace_docs_ace(items, from_ace, to_ace):
    """ Replace ``from_ace`` with ``to_ace`` in each ``items``.

    Look into ACLEncoderMixin.stringify_acl for details on ace format.

    :param items: Db objects ACL of which should be updated.
    :param from_ace: Stringified ACL entry (ACE) to match agains.
    :param to_ace: Stringified ACL entry (ACE) ``from_ace`` should be
        replaced with.
    """
    for item in items:
        log.debug('Updating ACE in: {}'.format(str(item)))
        acl = deepcopy(item._acl or [])
        try:
            ace_index = acl.index(from_ace)
        except ValueError:
            log.warn('ACE {} not found in document: {}'.format(
                str(from_ace), str(item)))
            continue
        acl.pop(ace_index)
        acl.insert(ace_index, to_ace)
        item.update({'_acl': acl})
