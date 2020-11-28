# A hash function takes in a collection of attributes,
# and maps it to a pair (f,c).
# The f is a function mapping packets to just the relevant part of the keys
# (presumably via a hash).
# The c is a coupon number.
# f can equivalently be an index of a query number,
# which then gives a look up of the relevant key mapping.
# This pair can also be 0,
# indicating that no query got fired for this attribute set.

# Upon receiving a packet,
# we pass it through multiple hash functions.
# If none collect, we do nothing.
# If exactly one collects, we pull that one.
# If multiple collect, we:
#   A: Collect one chosen at random.
#   B: Collect one of two at random, do nothing otherwise.
#   C: Do nothing.
# The paper uses B.

import collections

Packet = collections.namedtuple('Packet', ['source', 'destination', 'timestamp'])

key_funcs = [
        lambda packet: packet.source,
        lambda packet: (packet.source, packet.destination),
        ]

def phash(key):
    v = hash(str(key))
    return (v % 2**8) / 2**8

def attr_dst(packet):
    val = phash(packet.destination)
    if val < 0.1:
        coupon = int(val*40)
        return ((key_funcs[0], 0, {"m":4, "n":4}), coupon)
    else:
        return (None, -1)

def attr_timestamp(packet):
    val = phash(packet.timestamp)
    if val < 0.5:
        coupon = int(val*10)
        return ((key_funcs[0], 1, {"m":5, "n":5}), coupon)
    elif val < 0.75:
        coupon = int((val-0.5)*16)
        return ((key_funcs[1], 2, {"m":4, "n":3}), coupon)
    else:
        return (None, -1)

attr_funcs = [
        attr_dst,
        attr_timestamp
        ]

def count(arr):
    return sum(arr)

def report_threshold(key):
    print("Key {} has reached the threshold!".format(key))

coupons = {}

def receive(packet):
    for attr_func in attr_funcs:
        key_data, coupon = attr_func(packet)
        if key_data is not None:
            key_func, query_num, key_params = key_data
            query_val = (query_num, key_func(packet))
            if query_val in coupons:
                coupons[query_val][coupon] = True
                if count(coupons[query_val]) >= key_params["n"]:
                    report_threshold(query_val)
            else:
                coupons[query_val] = [False]*key_params["m"]
                coupons[query_val][coupon] = True

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
    print("Receiving: {}...".format(p))
    receive(p)

print(coupons)
