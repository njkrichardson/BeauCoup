from objects import Packet, Query, SingleStandaloneSwitch

def parse_file(fname):
    return []


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
