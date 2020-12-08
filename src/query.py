from functools import partial
from collections import namedtuple, defaultdict
from typing import Union

from exceptions import InvalidConfigurationException

Query = namedtuple('Query', ['p', 'm', 'n', 'raw_query'])
RawQuery = namedtuple('RawQuery', ['key_index', 'attr_index', 'threshold', 'mean_activation', 'name'])

DEFAULT_QUERIES = dict(
        spreader=(lambda packet: packet.source, lambda packet: packet.destination), 
        heavy_hitter=(lambda packet: (packet.source, packet.destination), lambda packet: packet.timestamp)
        )

DEFAULT_QUERY_NAMES = list(DEFAULT_QUERIES.keys())

def default_query_configs(name: str): 
    key_funcs, attr_funcs = [], []
    if name is 'all': 
        key_funcs.extend(DEFAULT_QUERIES
                [query_type][0] for query_type in DEFAULT_QUERY_NAMES)
        attr_funcs.extend(DEFAULT_QUERIES
                [query_type][1] for query_type in DEFAULT_QUERY_NAMES) 
    elif args.query_class in DEFAULT_QUERY_NAMES: 
        key_funcs.append(DEFAULT_QUERIES[name][0])
        attr_funcs.append(DEFAULT_QUERIES[name][1])
    else: 
        raise(NotImplementedError)
    return key_funcs, attr_funcs
    
def gather_queries(queries):
    queries_by_attr = defaultdict(lambda: [])
    for q in queries:
        queries_by_attr[q.raw_query.attr_index].append(q)
    for attr_index in queries_by_attr:
        p_sum = 0.0
        for q in queries_by_attr[attr_index]:
            p_sum += q.p
        if p_sum > 1.0:
            raise InvalidConfigurationException("Coupon Probabilities Exceed 1")
    return queries_by_attr
