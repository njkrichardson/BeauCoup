from collections import defaultdict
import logging 

from compiler import compile_queries
from packet import parse_packet_stream
from query import RawQuery
from server import PMPServer, EchoServer, ZeroErrorServer
from switch import PMPSwitch, SingleStandaloneSwitch, ZeroErrorSwitch
from utils import table_size

logger = logging.getLogger(__name__) 
logger.setLevel(logging.WARNING)
try: 
    file_handler = logging.FileHandler('logs/simulate.log')
except:
    file_handler = logging.FileHandler('src/logs/simulate.log')
logger.addHandler(file_handler)

def temporary_alert_function(query : RawQuery, key):
    print('Query "{}" hit threshold for key {}'.format(query.name, key))

def build_zeroerror(key_funcs: list, attr_funcs: list, raw_queries, alert_func, n: int = 1):
    server = ZeroErrorServer(key_funcs, attr_funcs, raw_queries, alert_func)
    switches = [ZeroErrorSwitch(server) for i in range(n)]
    return switches, server

def build_standalone_switches(key_funcs: list, attr_funcs: list, raw_queries, alert_func, n: int = 1):
    server = EchoServer(alert_func)
    queries = compile_queries(raw_queries) 
    switches = [SingleStandaloneSwitch(server, key_funcs, attr_funcs, queries) for i in range(n)]
    return switches, server

def build_pmp(key_funcs: list, attr_funcs: list, raw_queries, alert_func, n: int = 1):
    queries = compile_queries(raw_queries)
    server = PMPServer(alert_func)
    switches = [PMPSwitch(server, key_funcs, attr_funcs, queries) for i in range(n)]
    return switches, server

def manifest_world(builder: callable, key_funcs : list, attr_funcs : list, raw_queries : list, n_switches: int, n_packets: int): 
    truth_table = defaultdict(lambda: defaultdict(lambda: set()))

    alerts_list = []
    hits = defaultdict(lambda: set())
    def alert_logger(query : RawQuery, key):
        alerts_list.append((query.name, key, len(truth_table[query.name][key]), query.threshold))
        hits[query.name].add(key)

    switches, server = builder(key_funcs, attr_funcs, raw_queries, alert_logger, n_switches)
    packets = parse_packet_stream(n_packets=n_packets)

    i = 0

    for packet in packets:
        logger.debug(f"Receiving: {packet}...")
        for query in raw_queries:
            truth_table[query.name][key_funcs[query.key_index](packet)].add(attr_funcs[query.attr_index](packet))
        switches[i].receive(packet) #TODO we need a packet switching method (this can be a special case) 
        i += 1
        i = i % n_switches

    print("Alerts Triggered:")
    print(alerts_list)

    missed_alerts = []
    for query in raw_queries:
        for key in truth_table[query.name]:
            if len(truth_table[query.name][key]) >= query.threshold and not (key in hits[query.name]):
                missed_alerts.append((query.name, key, len(truth_table[query.name][key]), query.threshold))

    print("Alerts Missed:")
    print(missed_alerts)

    if hasattr(server, "coupons"):
        print("Memory Used: {}".format(table_size(server.coupons)))
    print("Messages Used: {}".format(server.message_count))

build_functions = {
        "Standalone": build_standalone_switches,
        "ZeroError": build_zeroerror,
        "PMP": build_pmp,
        }
