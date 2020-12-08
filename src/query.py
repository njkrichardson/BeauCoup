from collections import namedtuple, defaultdict

from exceptions import InvalidConfigurationException

Query = namedtuple('Query', ['key_index', 'attr_index', 'p', 'm', 'n', 'name'])
Conf = namedtuple('Configuration', ['q', 'key_func', 'p', 'm', 'n', 'query_name'])
RawQuery = namedtuple('RawQuery', ['key_index', 'attr_index', 'threshold', 'mean_activation', 'name'])

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
