import collections
import random

from compiler import compile_queries
from packet import Packet, parse_packet_stream
from query import Query, RawQuery, convert_queries, Conf
from utils import phash, count, flip_coin

debug = False #TODO logging

class BaseSwitch:
    def __init__(self, key_funcs, attr_funcs, queries):
        self.proc_by_attr_funcs = convert_queries(key_funcs, attr_funcs, queries)
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

    def select_key_and_coupon(self, packet):
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
        return chosen_query, coupon

    def update_coupon_table(self, chosen_query, coupon, packet):
        if chosen_query is not None:
            q = chosen_query.q
            if q not in self.coupons:
                self.coupons[q] = {}

            key_val = chosen_query.key_func(packet)
            if key_val in self.coupons[q]:
                self.coupons[q][key_val][1][coupon] = True
                if count(self.coupons[q][key_val][1]) >= chosen_query.n and not self.coupons[q][key_val][0]:
                    self.report_key(chosen_query.query_name, key_val)
                    self.coupons[q][key_val][0] = True
            else:
                self.coupons[q][key_val] = [False, [False]*chosen_query.m]
                self.coupons[q][key_val][1][coupon] = True

    def receive(self, packet):
        chosen_query, coupon = self.select_key_and_coupon(packet)
        self.update_coupon_table(chosen_query, coupon, packet)

    def reset(self):
        self.coupons = {}

    def report_key(self, *args):
        raise NotImplementedError("Switch class does not implement message sending")

class BaseServer:
    def __init__(self, *args):
        self.message_count = 0

    def receive_message(self, *args):
        self.message_count += 1
        self._receive_message(*args)

    def _receive_message(self, *args):
        raise NotImplementedError("Server class does not implement message reception.")

# =======
# Some basic implementations:
# All these do is run the earlier code and do some printing.
# No additional logic.
class SingleStandaloneSwitch(BaseSwitch):
    def report_key(self, query_name, key):
        print('Query "{}" hit threshold for key {}'.format(query_name, key))

class EchoServer(BaseServer):
    def _receive_message(self, message):
        print(message)

def build_standalone_switches(key_funcs, attr_funcs, raw_queries, n=1):
    queries = compile_queries(raw_queries)
    switches = [SingleStandaloneSwitch(key_funcs, attr_funcs, queries) for i in range(n)]
    server = EchoServer()
    return switches, server

# =======
# A theoretically correct solution,
# but one with massive memory and communication requirements.
# However, it gets the exact correct solution,
# so it is useful for comparison.
class ZeroErrorSwitch(BaseSwitch):
    def __init__(self, parent_server):
        self.parent_server = parent_server

    def receive(self, packet):
        self.parent_server.receive_message(packet)

class ZeroErrorServer(BaseServer):
    def __init__(self, key_funcs, attr_funcs, queries):
        super().__init__()
        self.key_funcs = key_funcs
        self.attr_funcs = attr_funcs
        self.queries = queries
        self.table = collections.defaultdict(lambda: collections.defaultdict(lambda: [False, set()]))

    def _receive_message(self, packet):
        for q in self.queries:
            kf = self.key_funcs[q.key_index]
            key = kf(packet)
            af = self.attr_funcs[q.attr_index]
            attr = af(packet)
            self.table[q.name][key][1].add(attr)
            if len(self.table[q.name][key][1]) > q.threshold and not self.table[q.name][key][0]:
                print('Query "{}" hit threshold for key {}'.format(q.name, key))
                self.table[q.name][key][0] = True

def build_zeroerror(key_funcs, attr_funcs, raw_queries, n=1):
    server = ZeroErrorServer(key_funcs, attr_funcs, raw_queries)
    switches = [ZeroErrorSwitch(server) for i in range(n)]
    return switches, server

# =======
# Probabilistical Message Passing:
# The switches in this model hash the packets,
# and then pass them on if they would be collected as a coupon.
# The individual switches use no memory,
# but the communication cost might be large.
class PMPSwitch(BaseSwitch):
    def __init__(self, parent_server, *args):
        super().__init__(*args)
        self.parent_server = parent_server

    def receive(self, packet):
        chosen_query, coupon = self.select_key_and_coupon(packet)

        if chosen_query is not None:
            q = chosen_query.q
            key_val = chosen_query.key_func(packet)
            self.report_key((chosen_query, key_val, coupon))

    def report_key(self, msg):
        self.parent_server.receive_message(msg)

class PMPServer(BaseServer):
    def __init__(self):
        super().__init__()
        self.coupons = {}

    def _receive_message(self, msg):
        cq, key_val, coupon = msg

        q = cq.q
        if q not in self.coupons:
            self.coupons[q] = {}

        if key_val in self.coupons[q]:
            self.coupons[q][key_val][1][coupon] = True
            if count(self.coupons[q][key_val][1]) >= cq.n and not self.coupons[q][key_val][0]:
                print('Query "{}" hit threshold for key {}'.format(cq.query_name, key_val))
                self.coupons[q][key_val][0] = True
        else:
            self.coupons[q][key_val] = [False, [False]*cq.m]
            self.coupons[q][key_val][1][coupon] = True

def build_pmp(key_funcs, attr_funcs, raw_queries, n=1):
    queries = compile_queries(raw_queries)
    server = PMPServer()
    switches = [PMPSwitch(server, key_funcs, attr_funcs, queries) for i in range(n)]
    return switches, server


# =======
build_functions = {
        "Standalone": build_standalone_switches,
        "ZeroError": build_zeroerror,
        "PMP": build_pmp,
        }

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

    raw_queries = [
            RawQuery(0, 1, 100, 0.1, 'Test'),
            ]

    n = 3
    switches, server = build_pmp(key_funcs, attr_funcs, raw_queries, n)
    # switches, server = build_zeroerror(key_funcs, attr_funcs, raw_queries, n)
    # switches, server = build_standalone_switches(key_funcs, attr_funcs, raw_queries, n)

    packets = parse_packet_stream(n_packets=10000)

    i = 0

    for p in packets:
        if debug:
            print("Receiving: {}...".format(p))
        switches[i].receive(p)
        i += 1
        i = i % n

    print(server.message_count)
    # for q in server.coupons:
    #     print("{}: {}".format(q, server.coupons[q]))
