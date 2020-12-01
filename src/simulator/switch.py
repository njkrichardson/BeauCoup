import collections
import random

debug = False

Packet = collections.namedtuple('Packet', ['source', 'destination', 'timestamp'])
Conf = collections.namedtuple('Configuration', ['q', 'key_func', 'p', 'm', 'n'])

key_funcs = [
        lambda packet: packet.source,
        lambda packet: (packet.source, packet.destination),
        ]

attr_funcs = [
        lambda packet: packet.destination,
        lambda packet: packet.timestamp,
        ]

proc_by_attr_funcs = [
        (attr_funcs[0], [
            Conf(0, key_funcs[0], 0.1, 4, 4),
            ]
            ),
        (attr_funcs[1], [
            Conf(1, key_funcs[0], 0.5, 5, 5),
            Conf(2, key_funcs[1], 0.25, 4, 3),
            ]
            ),
        ]

def phash(key):
    v = hash(str(key))
    return (v % 2**16) / 2**16

def proc_attr(packet, proc_by_attr_func):
    attr_func, confs = proc_by_attr_func
    val = phash(attr_func(packet))
    for c in confs:
        if val < c.p:
            coupon = int(val/c.p * c.m)
            return (c, coupon)
        val -= c.p
    return (None, 0)

def count(arr):
    return sum(arr)

def report_threshold(key):
    print("Key {} has reached the threshold!".format(key))

coupons = {}

def flip_coin():
    return bool(random.randint(0,1))

def receive(packet):
    chosen_query = None
    coupon = 0
    collected_coupons = 0

    for proc_by_attr_func in proc_by_attr_funcs:
        query_conf, sampled_coupon = proc_attr(packet, proc_by_attr_func)
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

    if debug:
        print("Coupons Collected: {}".format(collected_coupons))
        if chosen_query is not None:
            print("Updating query {} with coupon {}".format(chosen_query.q, coupon))

    if chosen_query is not None:
        query_val = (chosen_query.q, chosen_query.key_func(packet))
        if query_val in coupons:
            coupons[query_val][coupon] = True
            if count(coupons[query_val]) >= chosen_query.n:
                report_threshold(query_val)
        else:
            coupons[query_val] = [False]*chosen_query.m
            coupons[query_val][coupon] = True

if __name__ == "__main__":
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
        receive(p)

    print(coupons)
