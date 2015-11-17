"""
CLI to count number of documents that contain particular ACE.
Prints count of objects with matching ACE, listed by type.
"""

from argparse import ArgumentParser

from nefertari_guards.scripts.script_utils import AppBootstrapCmd


def main():
    return CountACECommand().run()


class CountACECommand(AppBootstrapCmd):
    """
    Usage example:
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
        pass
