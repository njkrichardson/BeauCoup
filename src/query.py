from functools import partial
from collections import namedtuple, defaultdict
from typing import Union

from exceptions import InvalidConfigurationException

Query = namedtuple('Query', ['key_index', 'attr_index', 'p', 'm', 'n', 'name'])
Conf = namedtuple('Configuration', ['q', 'key_func', 'p', 'm', 'n', 'query_name'])
RawQuery = namedtuple('RawQuery', ['key_index', 'attr_index', 'threshold', 'mean_activation', 'name'])

DEFAULT_QUERIES = dict(
        spreader=(lambda packet: packet.source, lambda packet: packet.destination), 
        heavy_hitter=(lambda packet: (packet.source, packet.destination), lambda packet: packet.timestamp)
        )

DEFAULT_QUERY_NAMES = list(DEFAULT_QUERIES.keys())

def default_query_configs(name: str): 
    key_funcs, attr_funcs = [], []
    if name is 'all': 
        key_funcs.extend(query_type[0] for query_type in DEFAULT_QUERY_NAMES)
        attr_funcs.extend(query_type[1] for query_type in DEFAULT_QUERY_NAMES) 
    elif args.query_class in DEFAULT_QUERY_NAMES: 
        key_funcs.append(DEFAULT_QUERIES[name][0])
        attr_funcs.append(DEFAULT_QUERIES[name][1])
    else: 
        raise(NotImplementedError)
    return key_funcs, attr_funcs
    
def convert_queries(key_funcs: list, attr_funcs: list, queries):
    query_by_attr = defaultdict(lambda: [])
    for i, q in enumerate(queries):
        query_by_attr[q.attr_index].append((i,q))
    proc_by_attr_funcs = []
    for attr_index in query_by_attr:
        try:
            attr_func = attr_funcs[attr_index]
        except IndexError:
            raise InvalidConfigurationException("Attribute Function Index Out Of Range")
        p_sum = 0.0
        query_confs = []
        for iq in query_by_attr[attr_index]:
            i, q = iq
            p_sum += q.p
            try:
                conf = Conf(i, key_funcs[q.key_index], q.p, q.m, q.n, q.name)
            except IndexError:
                raise InvalidConfigurationException("Key Function Index Out Of Range")
            query_confs.append(conf)
        if p_sum > 1.0:
            raise InvalidConfigurationException("Coupon Probabilities Exceed 1")
        proc_by_attr_funcs.append((attr_func, query_confs))
    return proc_by_attr_funcs
