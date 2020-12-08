import argparse 
import collections
import logging 
import random

import configure_paths
from packet import Packet, parse_packet_stream
from query import Query, RawQuery, default_query_configs
from utils import phash, count, flip_coin
from simulate import manifest_world, build_functions

SCHEMES = list(build_functions.values())

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
try: 
    file_handler = logging.FileHandler('logs/experiments/beaucoup_experiment.log')
except: 
    file_handler = logging.FileHandler('src/logs/experiments/beaucoup_experiment.log')

logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description='A standalone switch coupon collection problem; corresponds to the BeauCoup problem.') 
parser.add_argument('--query_class', type=str, default='mix', help='which class of query configurations to use (e.g., \'mix\', \'all\', \'spreader\')')
parser.add_argument('--n_switches', type=int, default=3, help='number of switches to simulate (a positive integer)')
parser.add_argument('--n_packets', type=int, default=int(10e4), help='number of packets to simulate (a positive integer)')
parser.add_argument('--system_type', type=str, default='Standalone', choices=build_functions.keys(), help='which system of servers and switches to simulate')
parser.add_argument('--n_queries', type=int, default=2, help='number of queries to use') 
args = parser.parse_args()

if __name__ == "__main__":
    n_packet_range = [int(10e2), int(10e3), int(10e4)]
    n_queries_range = [2, 10, 100] 
    for build_func in SCHEMES: 
        for n_packets in n_packet_range: 
            for n_queries in n_queries_range: 
                key_funcs, attr_funcs = default_query_configs(args.query_class, n_queries)

                raw_queries = [] 
                for i in range(n_queries): 
                    t_range = (500, 1500)
                    m_activation = random.random()
                    raw_queries.append(RawQuery(i, i, random.randint(*t_range), m_activation, 'name'))

                manifest_world(build_func, key_funcs, attr_funcs, raw_queries, args.n_switches, n_packets)
