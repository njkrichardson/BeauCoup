import collections
import random

debug = False

class InvalidConfigurationException(Exception):
    pass

Packet = collections.namedtuple('Packet', ['source', 'destination', 'timestamp'])
Conf = collections.namedtuple('Configuration', ['q', 'key_func', 'p', 'm', 'n', 'query_name'])
Query = collections.namedtuple('Query', ['key_index', 'attr_index', 'p', 'm', 'n', 'name'])


def phash(key):
    v = hash(str(key))
    return (v % 2**16) / 2**16

def count(arr):
    return sum(arr)

def flip_coin():
    return bool(random.randint(0,1))

class BaseSwitch:
    def __init__(self, key_funcs, attr_funcs, queries):
        self.proc_by_attr_funcs = BaseSwitch.convert_queries(key_funcs, attr_funcs, queries)
        self.coupons = {}

    @classmethod
    def convert_queries(cls, key_funcs, attr_funcs, queries):
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
                    conf = Conf(i, key_funcs[q.key_index], q.p, q.m, q.n, q.name)
                except IndexError:
                    raise InvalidConfigurationException("Key Function Index Out Of Range")
                query_confs.append(conf)
            if p_sum > 1.0:
                raise InvalidConfigurationException("Coupon Probabilities Exceed 1")
            proc_by_attr_funcs.append((attr_func, query_confs))
        return proc_by_attr_funcs

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
            q = chosen_query.q
            if q not in self.coupons:
                self.coupons[q] = {}

            key_val = chosen_query.key_func(packet)
            if key_val in self.coupons[q]:
                self.coupons[q][key_val][coupon] = True
                if count(self.coupons[q][key_val]) >= chosen_query.n:
                    self.report_key(chosen_query.query_name, key_val)
            else:
                self.coupons[q][key_val] = [False]*chosen_query.m
                self.coupons[q][key_val][coupon] = True

    def reset(self):
        self.coupons = {}

    def report_key(self, *args):
        raise NotImplementedError("Switch class does not implement message sending")

class BaseServer:
    def __init__(self, *args):
        pass

    def receive_message(self, *args):
        raise NotImplementedError("Server class does not implement message reception.")


# =======
class SingleStandaloneSwitch(BaseSwitch):
    def report_key(self, query_name, key):
        print('Query "{}" hit threshold for key {}'.format(query_name, key))

# =======

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
            Query(0, 0, 0.1, 4, 4, 'Spreaders'),
            Query(0, 1, 0.5, 5, 5, 'Heavy-Hitters'),
            Query(1, 1, 0.25, 4, 3, 'Heavy-Hitter Pairs'),
            ]


    s = SingleStandaloneSwitch(key_funcs, attr_funcs, queries)

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

    for q in s.coupons:
        print("{}: {}".format(q, s.coupons[q]))
