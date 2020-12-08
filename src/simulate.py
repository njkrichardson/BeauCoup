from collections import defaultdict
import logging 

from compiler import compile_queries
from packet import parse_packet_stream
from query import RawQuery
from server import PMPServer, EchoServer, ZeroErrorServer
from switch import PMPSwitch, SingleStandaloneSwitch, ZeroErrorSwitch

logger = logging.getLogger(__name__) 
logger.setLevel(logging.WARNING)
try: 
    file_handler = logging.FileHandler('logs/simulate.log')
except:
    file_handler = logging.FileHandler('src/logs/simulate.log')
logger.addHandler(file_handler)

def temporary_alert_function(query : RawQuery, key):
    print('Query "{}" hit threshold for key {}'.format(query.name, key))

def build_zeroerror(key_funcs: list, attr_funcs: list, raw_queries, n: int = 1):
    server = ZeroErrorServer(key_funcs, attr_funcs, raw_queries, temporary_alert_function)
    switches = [ZeroErrorSwitch(server) for i in range(n)]
    return switches, server

def build_standalone_switches(key_funcs: list, attr_funcs: list, raw_queries, n: int = 1):
    server = EchoServer(temporary_alert_function)
    queries = compile_queries(raw_queries) 
    switches = [SingleStandaloneSwitch(server, key_funcs, attr_funcs, queries) for i in range(n)]
    return switches, server

def build_pmp(key_funcs: list, attr_funcs: list, raw_queries, n: int = 1):
    queries = compile_queries(raw_queries)
    server = PMPServer(temporary_alert_function)
    switches = [PMPSwitch(server, key_funcs, attr_funcs, queries) for i in range(n)]
    return switches, server

def manifest_world(builder: callable, n_switches: int, n_packets: int): 
    switches, server = builder(n_switches)
    packets = parse_packet_stream(n_packets=n_packets)
    i = 0
    truth_table = defaultdict(lambda: defaultdict(lambda: set()))

    for packet in packets:
        logger.debug(f"Receiving: {packet}...")
        switches[i].receive(packet) #TODO we need a packet switching method (this can be a special case) 
        i += 1
        i = i % n_switches

    print(server.message_count)

build_functions = {
        "Standalone": build_standalone_switches,
        "ZeroError": build_zeroerror,
        "PMP": build_pmp,
        }
