from __future__ import absolute_import

from mongoengine import fields

from nefertari_mongodb.fields import BaseFieldMixin
from nefertari_mongodb.documents import TYPES_MAP

from .base import ACLEncoderMixin, ACL_TYPE_MAPPING


class ACLField(ACLEncoderMixin, BaseFieldMixin, fields.ListField):
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


""" Create full map of ES mappings including ACLField """
ACL_TYPE_MAP = {ACLField: ACL_TYPE_MAPPING}
EXTENDED_TYPES_MAP = dict(
    list(TYPES_MAP.items()) +
    list(ACL_TYPE_MAP.items())
)
