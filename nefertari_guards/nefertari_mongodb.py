from nefertari_mongodb.fields import ProcessableMixin, BaseFieldMixin
from mongoengine import fields

from .base import ACLEncoderMixin


class ACLField(ACLEncoderMixin, ProcessableMixin, BaseFieldMixin,
               fields.ListField):
    """ Subclass of `ListField` used to store Pyramid ACL.

    ACL is stored as nested list with all Pyramid special actions,
    identifieds and permissions converted to strings.
    """
    def __set__(self, instance, value):
        """ Convert Pyramid ACL objects into string representation,
        validate and store in mongo.
        """
        valid_value = value and isinstance(value, (list, tuple))
        if valid_value and isinstance(value[0], (list, tuple, dict)):
            value = self.stringify_acl(value)
            self.validate_acl(value)
        return super(ACLField, self).__set__(instance, value)
