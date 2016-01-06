import logging

from pyramid.paster import bootstrap
from nefertari.utils import dictset


class AppBootstrapCmd(object):
    """ Base command class that bootstraps app and logger. """
    def __init__(self):
        super(AppBootstrapCmd, self).__init__()
        self.options = self._parse_options()
        self._setup_logger()
        self._bootstrap(self.options)

    def _parse_options(self):
        """ Parse command line arguments and return result. """
        raise NotImplementedError

    def _setup_logger(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.ERROR)
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - {} - %(message)s'.format(__name__))
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

    def _bootstrap(self, options):
        """ Bootstrap app. """
        env = bootstrap(options.config)
        self.registry = env['registry']
        self.settings = dictset(self.registry.settings)
