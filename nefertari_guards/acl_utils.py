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
from nefertari import engine
from nefertari.elasticsearch import ES


def count_ace(ace, types=None):
    return find_by_ace(ace, types, count=True)


def update_ace(from_ace, to_ace, types=None):
    documents = find_by_ace(from_ace, types)


def find_by_ace(ace, types=None, count=False):
    if types is None:
        types = list(engine.get_document_classes().values())
    es_types = _get_es_types(types)

    params = {'body': _get_es_body(ace)}
    if count:
        params['_count'] = True

    return ES(es_types).get_collection(**params)


def _get_es_types(types):
    type_names = [t.__name__ for t in types
                  if getattr(t, '_index_enabled', False)]
    es_types = [ES.src2type(name) for name in type_names]
    return ','.join(es_types)


def _get_es_body(ace):
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
