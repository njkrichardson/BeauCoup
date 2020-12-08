from collections import defaultdict 

from utils import count 

class BaseServer:
    def __init__(self, *args):
        self.message_count = 0

    def receive_message(self, *args):
        self.message_count += 1
        self._receive_message(*args)

    def _receive_message(self, *args):
        raise NotImplementedError("Server class does not implement message reception.")

class EchoServer(BaseServer):
    def _receive_message(self, message):
        print(message)


class ZeroErrorServer(BaseServer):
    def __init__(self, key_funcs, attr_funcs, queries):
        super().__init__()
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
                print('Query "{}" hit threshold for key {}'.format(q.name, key)) # TODO: logging 
                self.table[q.name][key][0] = True

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
