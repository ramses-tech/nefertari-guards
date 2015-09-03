from pyramid.security import (
    Allow, Deny, Everyone, Authenticated, ALL_PERMISSIONS)
from nefertari.resource import PERMISSIONS as NEF_PERMISSIONS


""" Elasticsearch type mapping for ACLField """
ACL_TYPE_MAPPING = {
    'type': 'nested',
    'properties': {
        'action': {'type': 'string'},
        'principal': {'type': 'string', 'index': 'not_analyzed'},
        'permission': {'type': 'string'},
    }
}


class ACLEncoderMixin(object):
    """ Mixin which implements ACL encoding/decoding.

    Used in sqla and mongo ACLField.
    """
    ACTIONS = {
        Allow: 'allow',
        Deny: 'deny',
    }
    PRINCIPALS = {
        Everyone: 'everyone',
        Authenticated: 'authenticated',
    }
    PERMISSIONS = {
        str(ALL_PERMISSIONS): 'all',
    }
    PERMISSIONS_INVERTED = {
        'all': ALL_PERMISSIONS,
    }

    def _validate_action(self, action):
        """ Validate :action: has allowed value.

        :param action: String representation of Pyramid ACL action.
        """
        valid_actions = self.ACTIONS.values()
        if action not in valid_actions:
            err = 'Invalid ACL action value: {}. Valid values are: {}'
            raise ValueError(err.format(action, ', '.join(valid_actions)))

    def _validate_permission(self, permission):
        """ Validate :permission: has allowed value.

        Valid permission is name of one of nefertari view methods or 'all'.
        :param permission: String representing ACL permission name.
        """
        valid_perms = set(self.PERMISSIONS.values())
        valid_perms.update(NEF_PERMISSIONS.values())
        if permission not in valid_perms:
            err = 'Invalid ACL permission value: {}. Valid values are: {}'
            raise ValueError(err.format(permission, ', '.join(valid_perms)))

    def validate_acl(self, value):
        """ Validate ACL elements.

        Identifiers are not validated as they may be arbitrary strings.
        """
        for ac_entry in value:
            self._validate_action(ac_entry['action'])
            self._validate_permission(ac_entry['permission'])

    @classmethod
    def _stringify_action(cls, action):
        """ Convert Pyramid ACL action object to string. """
        action = cls.ACTIONS.get(action, action)
        return action.strip().lower()

    @classmethod
    def _stringify_principal(cls, principal):
        """ Convert to string specific ACL principals if any are
        present.
        """
        return cls.PRINCIPALS.get(principal, principal)

    @classmethod
    def _stringify_permissions(cls, permissions):
        """ Convert to string special ACL permissions if any present.

        If :permissions: is wrapped in list if it's not already a list
        or tuple.
        """
        if not isinstance(permissions, (list, tuple)):
            permissions = [permissions]
        clean_permissions = []
        for permission in permissions:
            try:
                permission = permission.strip().lower()
            except AttributeError:
                pass
            clean_permissions.append(permission)
        return [cls.PERMISSIONS.get(str(perm), perm)
                for perm in clean_permissions]

    @classmethod
    def stringify_acl(cls, value):
        """ Get valid Pyramid ACL and translate values to strings.

        String cleaning and case conversion is also performed here.
        In case ACL is already converted it won't change. Input ACL is
        also flattened to include a singler permission per AC entry.

        Structure of result AC entries is:
            {'action': '...', 'principal': '...', 'permission': '...'}
        """
        string_acl = []
        if value is None:
            return string_acl
        for ac_entry in value:
            if isinstance(ac_entry, dict):  # ACE is already in DB format
                string_acl.append(ac_entry)
                continue
            action, principal, permissions = ac_entry
            action = cls._stringify_action(action)
            principal = cls._stringify_principal(principal)
            permissions = cls._stringify_permissions(permissions)
            for perm in permissions:
                string_acl.append({
                    'action': action,
                    'principal': principal,
                    'permission': perm,
                })
        return string_acl

    @classmethod
    def _objectify_action(cls, action):
        """ Convert string representation of action into valid
        Pyramid ACL action.
        """
        inverted_actions = {v: k for k, v in cls.ACTIONS.items()}
        return inverted_actions[action]

    @classmethod
    def _objectify_principal(cls, principal):
        """ Convert string representation if special Pyramid principals
        into valid Pyramid ACL indentifier objects.
        """
        inverted_principals = {v: k for k, v in cls.PRINCIPALS.items()}
        return inverted_principals.get(principal, principal)

    @classmethod
    def _objectify_permission(cls, permission):
        """ Convert string representation if special Pyramid permission
        into valid Pyramid ACL permission objects.
        """
        return cls.PERMISSIONS_INVERTED.get(permission, permission)

    @classmethod
    def objectify_acl(cls, value):
        """ Convert string representation of ACL into valid Pyramid ACL. """
        object_acl = []
        if value is None:
            return object_acl
        for ac_entry in value:
            action = cls._objectify_action(ac_entry['action'])
            principal = cls._objectify_principal(ac_entry['principal'])
            permission = cls._objectify_permission(ac_entry['permission'])
            object_acl.append([action, principal, permission])
        return object_acl
