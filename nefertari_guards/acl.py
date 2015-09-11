class DatabaseACLMixin(object):
    """ ACL mixin class to be used when storing ACLs in DB. """

    def __init__(self, request):
        """ Copy `self.__acl__` to `item_model.__item_acl__` attribute """
        model = self.item_model
        if model is not None and model.__item_acl__ is None:
            model.__item_acl__ = self.__acl__
        super(DatabaseACLMixin, self).__init__(request)

    def item_acl(self, item):
        return item.get_acl()
