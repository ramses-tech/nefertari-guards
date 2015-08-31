import pytest
from mock import patch

from pyramid.security import (
    Allow, Deny, Everyone, Authenticated, ALL_PERMISSIONS)

from .base import ACLEncoderMixin, NEF_ACTIONS


class TestACLEncoderMixin(object):
    def test_validate_action_valid(self):
        obj = ACLEncoderMixin()
        try:
            obj._validate_action(list(obj.ACTIONS.values())[0])
        except ValueError:
            raise Exception('Unexpected error')

    def test_validate_action_invalid(self):
        obj = ACLEncoderMixin()
        with pytest.raises(ValueError) as ex:
            obj._validate_action('foobarbaz')
        expected = 'Invalid ACL action value: foobarbaz. Valid values are:'
        assert expected in str(ex.value)

    def test_validate_permission_valid(self):
        obj = ACLEncoderMixin()
        try:
            obj._validate_permission(NEF_ACTIONS[0])
        except ValueError:
            raise Exception('Unexpected error')

    def test_validate_permission_invalid(self):
        obj = ACLEncoderMixin()
        with pytest.raises(ValueError) as ex:
            obj._validate_permission('foobarbaz')
        expected = 'Invalid ACL permission value: foobarbaz. Valid values are:'
        assert expected in str(ex.value)

    @patch.object(ACLEncoderMixin, '_validate_action')
    @patch.object(ACLEncoderMixin, '_validate_permission')
    def test_validate_acl(self, mock_perm, mock_action):
        obj = ACLEncoderMixin()
        obj.validate_acl([{'action': 1, 'identifier': 2, 'permission': 3}])
        mock_action.assert_called_once_with(1)
        mock_perm.assert_called_once_with(3)

    def test_stringify_action_existing(self):
        obj = ACLEncoderMixin()
        assert obj._stringify_action(Deny) == 'deny'
        assert obj._stringify_action(Allow) == 'allow'

    def test_stringify_action_nonexisting(self):
        obj = ACLEncoderMixin()
        assert obj._stringify_action('not allow') == 'not allow'

    def test_stringify_identifier_special(self):
        obj = ACLEncoderMixin()
        assert obj._stringify_identifier(Everyone) == 'everyone'
        assert obj._stringify_identifier(Authenticated) == 'authenticated'

    def test_stringify_identifier(self):
        obj = ACLEncoderMixin()
        assert obj._stringify_identifier('g:admin') == 'g:admin'

    def test_stringify_permissions_regular_string(self):
        obj = ACLEncoderMixin()
        assert obj._stringify_permissions('Foo  ') == ['foo']

    def test_stringify_permissions_special(self):
        obj = ACLEncoderMixin()
        perms = obj._stringify_permissions(['foo', ALL_PERMISSIONS])
        assert sorted(perms) == ['all', 'foo']

    @patch.object(ACLEncoderMixin, '_stringify_action')
    @patch.object(ACLEncoderMixin, '_stringify_identifier')
    @patch.object(ACLEncoderMixin, '_stringify_permissions')
    def test_stringify_acl(self, mock_perm, mock_id, mock_action):
        obj = ACLEncoderMixin()
        mock_action.return_value = 1
        mock_id.return_value = 2
        mock_perm.return_value = [3, 4]
        result = obj.stringify_acl([('a', 'b', 'c')])
        assert result == [
            {'action': 1, 'identifier': 2, 'permission': 3},
            {'action': 1, 'identifier': 2, 'permission': 4},
        ]
        mock_action.assert_called_once_with('a')
        mock_id.assert_called_once_with('b')
        mock_perm.assert_called_once_with('c')

    def test_objectify_action(self):
        assert ACLEncoderMixin._objectify_action('allow') is Allow
        assert ACLEncoderMixin._objectify_action('deny') is Deny

    def test_objectify_identifier(self):
        assert ACLEncoderMixin._objectify_identifier(
            'everyone') is Everyone
        assert ACLEncoderMixin._objectify_identifier(
            'authenticated') is Authenticated
        assert ACLEncoderMixin._objectify_identifier('foo') == 'foo'

    def test_objectify_permission(self):
        assert ACLEncoderMixin._objectify_permission(
            'all') == ALL_PERMISSIONS
        assert ACLEncoderMixin._objectify_permission('foo') == 'foo'

    @patch.object(ACLEncoderMixin, '_objectify_action')
    @patch.object(ACLEncoderMixin, '_objectify_identifier')
    @patch.object(ACLEncoderMixin, '_objectify_permission')
    def test_objectify_acl(self, mock_perm, mock_id, mock_action):
        mock_action.return_value = 1
        mock_id.return_value = 2
        mock_perm.return_value = [3]
        result = ACLEncoderMixin.objectify_acl([
            {'action': 'a', 'identifier': 'b', 'permission': 'c'}
        ])
        assert result == [[1, 2, [3]]]
        mock_action.assert_called_once_with('a')
        mock_id.assert_called_once_with('b')
        mock_perm.assert_called_once_with('c')
