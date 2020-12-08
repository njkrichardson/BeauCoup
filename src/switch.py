from compiler import compile_queries
from query import convert_queries 
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

class SingleStandaloneSwitch(BaseSwitch):
    def report_key(self, query_name, key):
        print('Query "{}" hit threshold for key {}'.format(query_name, key))


class ZeroErrorSwitch(BaseSwitch):
    def __init__(self, parent_server):
        self.parent_server = parent_server

    def receive(self, packet):
        self.parent_server.receive_message(packet)

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

def build_standalone_switches(key_funcs: list, attr_funcs: list, raw_queries, n: int = 1):
    queries = compile_queries(raw_queries) 
    switches = [SingleStandaloneSwitch(key_funcs, attr_funcs, queries) for i in range(n)]
    server = EchoServer()
    return switches, server
