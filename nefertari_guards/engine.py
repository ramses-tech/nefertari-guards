from zope.dottedname.resolve import resolve


def includeme(config):
    """ Extend module globals with engine-specific objects from
    local nefertari_sqla or nefertari_mongodb modules.
    """
    from .documents import get_document_mixin

    def _valid_global(g):
        ignored = ('log', 'includeme')
        return (not g.startswith('__') and g not in ignored)

    engine_path = config.registry.settings['nefertari.engine']
    engine_module = resolve('nefertari_guards.' + engine_path)
    engine_globals = {k: v for k, v in engine_module.__dict__.items()
                      if _valid_global(k)}
    engine_globals['DocumentACLMixin'] = get_document_mixin(
        engine_module)
    globals().update(engine_globals)
