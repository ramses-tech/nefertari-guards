def get_document_mixin(engine_module):
    """ Define and return DocumentACLMixin """

    import logging
    log = logging.getLogger(__name__)

    class DocumentACLMixin(object):
        """ Document mixin that contains all needed methods to support
        storing ACLs in database and retrieving them.
        """
        __item_acl__ = None
        _acl = engine_module.ACLField()

        @classmethod
        def default_item_acl(cls):
            """ Return `cls.__item_acl__` which is used as a default
            item ACL if other ACLs is not explicitly provided.
            """
            return cls.__item_acl__

        def get_acl(self):
            """ Convert stored ACL to valid Pyramid ACL. """
            acl = engine_module.ACLField.objectify_acl(self._acl)
            log.info('Loaded ACL from database for {}({}): {}'.format(
                self.__class__.__name__,
                getattr(self, self.pk_field()), acl))
            return acl

        def _set_default_acl(self):
            """ Set default object ACL if not already set. """
            if self._is_created() and not self._acl:
                acl = self.default_item_acl()
                self._acl = engine_module.ACLField.stringify_acl(acl)

        def save(self, *args, **kwargs):
            """ Override to call `self._set_default_acl` """
            self._set_default_acl()
            return super(DocumentACLMixin, self).save(*args, **kwargs)

        @classmethod
        def get_es_mapping(cls, types_map=None, **kwargs):
            """ Generate ES mapping from model schema. """
            return super(DocumentACLMixin, cls).get_es_mapping(
                types_map=engine_module.EXTENDED_TYPES_MAP, **kwargs)

    return DocumentACLMixin
