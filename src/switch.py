from compiler import compile_queries
from query import gather_queries 
from utils import phash, count, flip_coin

class BaseSwitch:
    def __init__(self, parent_server, key_funcs, attr_funcs, queries):
        self.parent_server = parent_server
        self.key_funcs = key_funcs
        self.attr_funcs = attr_funcs
        self.queries = queries
        self.queries_by_attr = gather_queries(queries)
        self.coupons = {}

    def select_key_and_coupon(self, packet):
        chosen_coupons = []

        for attr_index in self.queries_by_attr:
            grouped_queries = self.queries_by_attr[attr_index]
            attr_func = self.attr_funcs[attr_index]
            val = phash(attr_func(packet))
            for query in grouped_queries:
                if val < query.p:
                    coupon = int(val/query.p * query.m)
                    chosen_coupons += [(query, coupon),]
                    break
                val -= query.p

        if len(chosen_coupons) == 1:
            return chosen_coupons[0]

        if len(chosen_coupons) == 2:
            return chosen_coupons[1] if flip_coin() else chosen_coupons[0]

        return (None, 0)

    def update_coupon_table(self, query, coupon, packet):
        query_name = query.raw_query.name
        if query_name not in self.coupons:
            self.coupons[query_name] = {}

        key_val = self.key_funcs[query.raw_query.key_index](packet)
        if key_val not in self.coupons[query_name]:
            self.coupons[query_name][key_val] = [False, [False]*query.m]

        self.coupons[query_name][key_val][1][coupon] = True
        if count(self.coupons[query_name][key_val][1]) >= query.n and not self.coupons[query_name][key_val][0]:
            self.report_key(query, key_val)
            self.coupons[query_name][key_val][0] = True

    def receive(self, packet):
        chosen_query, coupon = self.select_key_and_coupon(packet)
        if chosen_query is not None:
            self.update_coupon_table(chosen_query, coupon, packet)

    def reset(self):
        self.coupons = {}

    def report_key(self, *args):
        raise NotImplementedError("Switch class does not implement message sending")

class SingleStandaloneSwitch(BaseSwitch):
    def report_key(self, query, key):
        self.parent_server.receive_message(query, key)

class ZeroErrorSwitch(BaseSwitch):
    def __init__(self, parent_server, *args):
        self.parent_server = parent_server

    def receive(self, packet):
        self.parent_server.receive_message(packet)

class PMPSwitch(BaseSwitch):
    def receive(self, packet):
        chosen_query, coupon = self.select_key_and_coupon(packet)

        if chosen_query is not None:
            key_val = self.key_funcs[chosen_query.raw_query.key_index](packet)
            self.report_key((chosen_query, key_val, coupon))

    def report_key(self, msg):
        self.parent_server.receive_message(msg)

def build_standalone_switches(key_funcs: list, attr_funcs: list, raw_queries, n: int = 1):
    server = EchoServer()
    queries = compile_queries(raw_queries)
    switches = [SingleStandaloneSwitch(server, key_funcs, attr_funcs, queries) for i in range(n)]
    return switches, server

