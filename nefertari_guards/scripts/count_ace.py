"""
count_ace:
    Count the number of documents that contain a particular ACE.
    Prints the count of objects with matching ACE, listed by type, in CSV format.
"""
import json
from argparse import ArgumentParser

import six
from nefertari import engine
from nefertari.utils import split_strip

from nefertari_guards.scripts.script_utils import AppBootstrapCmd
from nefertari_guards.acl_utils import count_ace


def main():
    return CountACECommand().run()


class CountACECommand(AppBootstrapCmd):
    """
    :Usage example:
        $ nefertari-guards.count_ace
        --config=local.ini
        --ace='{"action": "allow", "principal": "user1", "permission": "view"}'
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
            '--ace',
            help=('JSON-encoded ACE to use in documents lookup.'),
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
            ace = json.loads(self.options.ace)
        except ValueError as ex:
            raise ValueError('--ace: {}'.format(ex))

        counts = count_ace(ace=ace, models=models)
        six.print_('Model,Count')
        for model, count in counts.items():
            if count is None:
                count = 'Not es-based'
            six.print_('{},{}'.format(model.__name__, count))
