import pytest
from mock import patch, Mock, call

from nefertari_guards.scripts.count_ace import CountACECommand


@patch('nefertari_guards.scripts.count_ace.CountACECommand._parse_options')
@patch('nefertari_guards.scripts.count_ace.CountACECommand._bootstrap')
class TestCountACECommand(object):

    @patch('nefertari_guards.scripts.count_ace.engine')
    def test_run_wrong_ace_format(self, mock_eng, mock_boot, mock_parse):
        obj = CountACECommand()
        obj.options = Mock(ace='asdasdasdasd', models='User,Story')
        with pytest.raises(ValueError) as ex:
            obj.run()
        assert '--ace' in str(ex.value)
        mock_eng.get_document_cls.assert_has_calls([
            call('User'), call('Story')])

    @patch('nefertari_guards.scripts.count_ace.count_ace')
    def test_run_no_models(
            self, mock_count, mock_boot, mock_parse):
        obj = CountACECommand()
        obj.options = Mock(ace='{}', models=None)
        mock_count.return_value = {Mock(__name__='Foo'): 1}
        obj.run()
        mock_count.assert_called_once_with(ace={}, models=None)

    @patch('nefertari_guards.scripts.count_ace.count_ace')
    @patch('nefertari_guards.scripts.count_ace.six')
    def test_run_none_count(
            self, mock_six, mock_count, mock_boot, mock_parse):
        obj = CountACECommand()
        obj.options = Mock(ace='{}', models='')
        mock_count.return_value = {Mock(__name__='Foo'): None}
        obj.run()
        mock_six.print_.assert_has_calls([
            call('Model,Count'),
            call('Foo,Not es-based'),
        ])

    @patch('nefertari_guards.scripts.count_ace.engine')
    @patch('nefertari_guards.scripts.count_ace.count_ace')
    @patch('nefertari_guards.scripts.count_ace.six')
    def test_run(
            self, mock_six, mock_count, mock_eng, mock_boot,
            mock_parse):
        obj = CountACECommand()
        obj.options = Mock(ace='{}', models='User')
        model = Mock(__name__='Foo')
        mock_eng.get_document_cls.return_value = model
        mock_count.return_value = {model: 123}
        obj.run()
        mock_six.print_.assert_has_calls([
            call('Model,Count'),
            call('Foo,123'),
        ])
        mock_count.assert_called_once_with(ace={}, models=[model])
