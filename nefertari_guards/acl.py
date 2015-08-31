class DatabaseACLMixin(object):
    def __init__(self, request):
        model = self.item_model
        if model is not None and model.__item_acl__ is None:
            model.__item_acl__ = self.__acl__
        super(DatabaseACLMixin, self).__init__(request)

    def item_acl(self, item):
        return item.get_acl()
