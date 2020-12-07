from collections import namedtuple

Query = namedtuple('Query', ['key_index', 'attr_index', 'p', 'm', 'n', 'name'])
RawQuery = namedtuple('RawQuery', ['key_index', 'attr_index', 'threshold', 'mean_activation', 'name'])

