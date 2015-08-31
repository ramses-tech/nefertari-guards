import logging

log = logging.getLogger(__name__)


class DocumentACLMixin(object):
    __abstract__ = True
    meta = {'abstract': True}

    __item_acl__ = None
    _acl = ACLField()

    @classmethod
    def default_item_acl(cls):
        return cls.__item_acl__

    def get_acl(self):
        """ Convert stored ACL to valid Pyramid ACL. """
        acl = ACLField.objectify_acl(self._acl)
        log.info('Loaded ACL from database for {}({}): {}'.format(
            self.__class__.__name__,
            getattr(self, self.pk_field()), acl))
        return acl

    def _set_default_acl(self):
        """ Set default object ACL if not already set. """
        if self._is_created() and not self._acl:
            self._acl = self.default_item_acl()

    def save(self, *args, **kwargs):
        self._set_default_acl()
        return super(DocumentACLMixin, self).save(*args, **kwargs)
