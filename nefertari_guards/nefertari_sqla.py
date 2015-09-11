from __future__ import absolute_import

from sqlalchemy_utils.types.json import JSONType
from nefertari_sqla.fields import BaseField
from nefertari_sqla.documents import TYPES_MAP

from .base import ACLEncoderMixin, ACL_TYPE_MAPPING


class ACLType(ACLEncoderMixin, JSONType):
    """ Subclass of `JSONType` used to store Pyramid ACL.

    ACL is stored as nested list with all Pyramid special actions,
    identifieds and permissions converted to strings.
    """
    def process_bind_param(self, value, dialect):
        """ Convert Pyramid ACL objects into string representation,
        validate and store in DB as JSON.
        """
        value = self.stringify_acl(value)
        self.validate_acl(value)
        return super(ACLType, self).process_bind_param(value, dialect)


class ACLField(ACLEncoderMixin, BaseField):
    """ Field used to store Pyramid ACLs. """
    _sqla_type_cls = ACLType
    _type_unchanged_kwargs = ()

    def process_type_args(self, kwargs):
        type_args, type_kw, cleaned_kw = super(
            ACLField, self).process_type_args(kwargs)
        cleaned_kw['default'] = cleaned_kw.get('default') or []
        return type_args, type_kw, cleaned_kw


""" Create full map of ES mappings including ACLField """
ACL_TYPE_MAP = {ACLType: ACL_TYPE_MAPPING}
EXTENDED_TYPES_MAP = dict(
    list(TYPES_MAP.items()) +
    list(ACL_TYPE_MAP.items())
)
