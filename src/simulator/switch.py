import collections
import random

debug = False

class InvalidConfigurationException(Exception):
    pass

Packet = collections.namedtuple('Packet', ['source', 'destination', 'timestamp'])
Conf = collections.namedtuple('Configuration', ['q', 'key_func', 'p', 'm', 'n'])
Query = collections.namedtuple('Query', ['key_index', 'attr_index', 'p', 'm', 'n'])

def convert_queries(key_funcs, attr_funcs, queries):
    query_by_attr = collections.defaultdict(lambda: [])
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
                conf = Conf(i, key_funcs[q.key_index], q.p, q.m, q.n)
            except IndexError:
                raise InvalidConfigurationException("Key Function Index Out Of Range")
            query_confs.append(conf)
        if p_sum > 1.0:
            raise InvalidConfigurationException("Coupon Probabilities Exceed 1")
        proc_by_attr_funcs.append((attr_func, query_confs))
    return proc_by_attr_funcs

def phash(key):
    v = hash(str(key))
    return (v % 2**16) / 2**16

def count(arr):
    return sum(arr)

def flip_coin():
    return bool(random.randint(0,1))

class Switch:
    def __init__(self, key_funcs, attr_funcs, queries, report_func):
        self.proc_by_attr_funcs = convert_queries(key_funcs, attr_funcs, queries)
        self.report_func = report_func
        self.coupons = {}

    def proc_attr(self, packet, proc_by_attr_func):
        attr_func, confs = proc_by_attr_func
        val = phash(attr_func(packet))
        for c in confs:
            if val < c.p:
                coupon = int(val/c.p * c.m)
                return (c, coupon)
            val -= c.p
        return (None, 0)

    def receive(self, packet):
        chosen_query = None
        coupon = 0
        collected_coupons = 0

        for proc_by_attr_func in self.proc_by_attr_funcs:
            query_conf, sampled_coupon = self.proc_attr(packet, proc_by_attr_func)
            if query_conf is not None:
                if collected_coupons == 0:
                    chosen_query = query_conf
                    coupon = sampled_coupon
                    collected_coupons += 1
                elif collected_coupons == 1:
                    if flip_coin():
                        chosen_query = query_conf
                        coupon = sampled_coupon
                    collected_coupons += 1
                else:
                    chosen_query = None
                    coupon = 0
                    collected_coupons += 1
                    break

        if chosen_query is not None:
            query_val = (chosen_query.q, chosen_query.key_func(packet))
            if query_val in self.coupons:
                self.coupons[query_val][coupon] = True
                if count(self.coupons[query_val]) >= chosen_query.n:
                    self.report_func()
            else:
                self.coupons[query_val] = [False]*chosen_query.m
                self.coupons[query_val][coupon] = True

    def reset(self):
        self.coupons = {}

if __name__ == "__main__":
    key_funcs = [
            lambda packet: packet.source,
            lambda packet: (packet.source, packet.destination),
            ]

    attr_funcs = [
            lambda packet: packet.destination,
            lambda packet: packet.timestamp,
            ]

    queries = [
            Query(0, 0, 0.1, 4, 4),
            Query(0, 1, 0.5, 5, 5),
            Query(1, 1, 0.25, 4, 3),
            ]

    report = lambda: print("Query Hit A Value!")

    s = Switch(key_funcs, attr_funcs, queries, report)

    packets = [
            Packet(100, 200, 300),
            Packet(100, 200, 400),
            Packet(100, 200, 500),
            Packet(100, 200, 600),
            Packet(100, 200, 700),
            Packet(100, 200, 800),
            Packet(100, 200, 900),
            Packet(100, 200, 1000),
            Packet(100, 300, 100),
            Packet(100, 300, 1100),
            Packet(100, 300, 1200),
            Packet(100, 300, 1300),
            Packet(100, 300, 1400),
            ]

    for p in packets:
        if debug:
            print("Receiving: {}...".format(p))
        s.receive(p)

    print(s.coupons)
