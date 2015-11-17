"""
CLI to find documents that contain particular ACE and replace that ACE
with another ACE.
"""

from argparse import ArgumentParser

from nefertari_guards.scripts.script_utils import AppBootstrapCmd


def main():
    return UpdateACECommand().run()


class UpdateACECommand(AppBootstrapCmd):
    """
    Usage example:
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
        pass
