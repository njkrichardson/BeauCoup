from collections import defaultdict 

from utils import count 

class BaseServer:
    def __init__(self, alert_func, *args):
        self.alert = alert_func
        self.message_count = 0

    def receive_message(self, *args):
        self.message_count += 1
        self._receive_message(*args)

    def _receive_message(self, *args):
        raise NotImplementedError("Server class does not implement message reception.")

class EchoServer(BaseServer):
    def _receive_message(self, query, key):
        self.alert(query.raw_query, key)

class ZeroErrorServer(BaseServer):
    def __init__(self, key_funcs, attr_funcs, queries, *args):
        super().__init__(*args)
        self.key_funcs = key_funcs
        self.attr_funcs = attr_funcs
        self.queries = queries
        self.table = defaultdict(lambda: defaultdict(lambda: [False, set()]))

    def _receive_message(self, packet):
        for q in self.queries:
            kf = self.key_funcs[q.key_index]
            key = kf(packet)
            af = self.attr_funcs[q.attr_index]
            attr = af(packet)
            self.table[q.name][key][1].add(attr)
            if len(self.table[q.name][key][1]) > q.threshold and not self.table[q.name][key][0]:
                self.alert(q, key)
                self.table[q.name][key][0] = True

class PMPServer(BaseServer):
    def __init__(self, *args):
        super().__init__(*args)
        self.coupons = {}

    def _receive_message(self, msg):
        query, key_val, coupon = msg
        query_name = query.raw_query.name
        if query_name not in self.coupons:
            self.coupons[query_name] = {}

        if key_val not in self.coupons[query_name]:
            self.coupons[query_name][key_val] = [False, [False]*query.m]

        self.coupons[query_name][key_val][1][coupon] = True
        if count(self.coupons[query_name][key_val][1]) >= query.n and not self.coupons[query_name][key_val][0]:
            self.alert(query.raw_query, key_val)
