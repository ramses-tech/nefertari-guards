import pytest
from mock import patch, Mock, call

from nefertari_guards.scripts.update_ace import UpdateACECommand


@patch('nefertari_guards.scripts.update_ace.UpdateACECommand._parse_options')
@patch('nefertari_guards.scripts.update_ace.UpdateACECommand._bootstrap')
class TestUpdateACECommand(object):

    @patch('nefertari_guards.scripts.update_ace.engine')
    def test_run_wrong_from_ace_format(self, mock_eng, mock_boot, mock_parse):
        obj = UpdateACECommand()
        obj.options = Mock(
            from_ace='asdasdasdasd', to_ace='{}', models='User,Story')
        with pytest.raises(ValueError) as ex:
            obj.run()
        assert '--from_ace' in str(ex.value)
        mock_eng.get_document_cls.assert_has_calls([
            call('User'), call('Story')])

    @patch('nefertari_guards.scripts.update_ace.engine')
    def test_run_wrong_to_ace_format(self, mock_eng, mock_boot, mock_parse):
        obj = UpdateACECommand()
        obj.options = Mock(
            from_ace='{}', to_ace='asdasdasdasd', models='User,Story')
        with pytest.raises(ValueError) as ex:
            obj.run()
        assert '--to_ace' in str(ex.value)
        mock_eng.get_document_cls.assert_has_calls([
            call('User'), call('Story')])

    @patch('nefertari_guards.scripts.update_ace.update_ace')
    def test_run_no_models(
            self, mock_count, mock_boot, mock_parse):
        obj = UpdateACECommand()
        obj.options = Mock(to_ace='{}', from_ace='{}', models=None)
        mock_count.return_value = {Mock(__name__='Foo'): 1}
        obj.run()
        mock_count.assert_called_once_with(
            to_ace={}, from_ace={}, models=None)

    @patch('nefertari_guards.scripts.update_ace.engine')
    @patch('nefertari_guards.scripts.update_ace.update_ace')
    def test_run(self, mock_count, mock_eng, mock_boot, mock_parse):
        obj = UpdateACECommand()
        obj.options = Mock(
            from_ace='{"a": 1}', to_ace='{"b": 2}', models='User')
        model = Mock(__name__='Foo')
        mock_eng.get_document_cls.return_value = model
        mock_count.return_value = {model: 123}
        obj.run()
        mock_count.assert_called_once_with(
            from_ace={"a": 1}, to_ace={"b": 2}, models=[model])
