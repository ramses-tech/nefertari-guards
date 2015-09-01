from mock import patch, Mock

from nefertari_guards.nefertari_sqla import ACLType


class TestACLType(object):

    @patch.object(ACLType, 'stringify_acl')
    @patch.object(ACLType, 'validate_acl')
    def test_process_bind_param(self, mock_validate, mock_str):
        mock_str.return_value = [[1, 2, [3]]]
        obj = ACLType()
        obj.process_bind_param([('a', 'b', 'c')], Mock())
        mock_str.assert_called_once_with([('a', 'b', 'c')])
        mock_validate.assert_called_once_with([[1, 2, [3]]])
