import re

from .cache import CacheAdapter
from .exception import ConfigException
from .utils import is_valid_hostname
from .agents import RequestsClient


class ApiContext(object):
    """
    Class defining the context of the sdk. It exposes configuration keys as attributes. Can be constructed optionally
    with a CacheAdapter instance
    """
    _DEFAULT_CONFIG = {'timeout': 20,
                       'verify_ssl': True}

    def __init__(self, hostname, config, cache=None):
        self.http_config = config.get('http', self._DEFAULT_CONFIG)
        self.hostname = hostname
        self.config = Config._init(self._build_config(config))
        if cache and not isinstance(cache, CacheAdapter):
            raise TypeError('Cache must be an instance of CacheAdapter')
        self.cache = cache
        self.client = self.build_client()

    def __getattr__(self, item):
        return getattr(self.config, item)

    def build_client(self):
        return RequestsClient(self.hostname, self.http_config)

    def _build_config(self, config_dict):
        return dict(config_dict, **{'hostname': self.hostname}, **self.http_config)


class Config(object):
    """
    Class abstracting sdk configuration.
    It performs validation on configuration keys and raises sdkboil.exception.ConfigException if any configuration
    value is invalid.
    """
    _CONFIG_DICT_KEYS = {'hostname', 'verify_ssl'}

    def __init__(self, **kwargs):
        self._config = kwargs

    @staticmethod
    def _init(kwargs):
        """
        Static constructor which performs validation on configuration keys, not accepting extra configuration keys
        and expecting every _CONFIG_DICT_KEYS name into initialization arguments
        """
        for key in Config._CONFIG_DICT_KEYS:
            if key not in kwargs.keys():
                raise ConfigException("{} missing from sdk configuration".format(key))
        return Config(**kwargs)

    def _validate(self):
        """
        Validates configuration values
        """
        self._validate_hostname()
        self._validate_ssl()

    def _validate_hostname(self):
        if not is_valid_hostname(self.hostname):
            raise ConfigException("{} is not a valid hostname".format(self.hostname))

    def _validate_ssl(self):
        if not isinstance(self.verify_ssl, bool):
            raise ConfigException("verify_ssl must be a boolean value, received {}".format(self.verify_ssl))

    def __getattr__(self, item):
        return self._config[item]
