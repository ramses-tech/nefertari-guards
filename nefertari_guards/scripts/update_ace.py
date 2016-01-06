"""
update_ace:
    Find documents that contain a particular ACE and replace that ACE
    with another ACE.
"""

import json
from argparse import ArgumentParser

import six
from nefertari import engine
from nefertari.utils import split_strip

from nefertari_guards.scripts.script_utils import AppBootstrapCmd
from nefertari_guards.acl_utils import update_ace


def main():
    return UpdateACECommand().run()


class UpdateACECommand(AppBootstrapCmd):
    """
    :Usage example:
        $ nefertari-guards.update_ace
        --config=local.ini
        --from_ace='{"action": "allow", "principal": "user1", "permission": "view"}'
        --to_ace='{"action": "deny", "principal": "user1", "permission": "view"}'
        --models=User,Story
    """
    def _parse_options(self):
        parser = ArgumentParser(description=__doc__)
        parser.add_argument(
            '-c', '--config',
            help='Config .ini file path',
            required=True)
        parser.add_argument(
            '--models',
            help=('Comma-separated list of model names which should be '
                  'affected. If not provided all es-based models '
                  'are used.'),
            required=False)
        parser.add_argument(
            '--from_ace',
            help=('JSON-encoded ACE to use in documents lookup.'),
            required=True)
        parser.add_argument(
            '--to_ace',
            help=('JSON-encoded ACE to replace "from_ace" ACE with.'),
            required=True)
        return parser.parse_args()

    def run(self):
        if self.options.models:
            model_names = split_strip(self.options.models)
            models = [engine.get_document_cls(name)
                      for name in model_names]
        else:
            models = None

        try:
            from_ace = json.loads(self.options.from_ace)
        except ValueError as ex:
            raise ValueError('--from_ace: {}'.format(ex))

        try:
            to_ace = json.loads(self.options.to_ace)
        except ValueError as ex:
            raise ValueError('--to_ace: {}'.format(ex))

        six.print_('Updating documents ACE')

        update_ace(from_ace=from_ace, to_ace=to_ace, models=models)

        try:
            import transaction
            transaction.commit()
        except:
            pass

        six.print_('Done')
