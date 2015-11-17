from mock import patch, Mock

from nefertari_guards.scripts import script_utils


@patch('nefertari_guards.scripts.script_utils.AppBootstrapCmd._parse_options')
class TestAppBootstrapCmd(object):

    @patch('nefertari_guards.scripts.script_utils.AppBootstrapCmd._setup_logger')
    @patch('nefertari_guards.scripts.script_utils.AppBootstrapCmd._bootstrap')
    def test_init(self, mock_boot, mock_set, mock_parse):
        obj = script_utils.AppBootstrapCmd()
        mock_parse.assert_called_once_with()
        mock_set.assert_called_once_with()
        mock_boot.assert_called_once_with(obj.options)

    @patch('nefertari_guards.scripts.script_utils.AppBootstrapCmd._setup_logger')
    @patch('nefertari_guards.scripts.script_utils.bootstrap')
    def test_bootstrap(self, mock_boot, mock_set, mock_parse):
        mock_parse.return_value = Mock(config=5)
        mock_boot.return_value = {'registry': Mock(settings={1: 2})}
        obj = script_utils.AppBootstrapCmd()
        assert obj.settings == {1: 2}
        mock_boot.assert_called_once_with(5)
        assert obj.registry == mock_boot()['registry']
