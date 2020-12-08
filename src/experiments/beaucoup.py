import argparse 
import collections
import logging 
import random
import pdb 

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
    results = () 
    n_packet_range = [int(1e2), int(1e3), int(1e4)]
    n_queries_range = [2] 
    for build_name, build_func in build_functions.items(): 
        for n_packets in n_packet_range: 
            for n_queries in n_queries_range: 
                key_funcs, attr_funcs = default_query_configs(args.query_class, n_queries)

                raw_queries = [] 
                for i in range(n_queries): 
                    t_range = (500, 1500)
                    m_activation = random.randint(20, 80)/100
                    raw_queries.append(RawQuery(i, i, random.randint(*t_range), m_activation, f'query_{i}'))

                memory_used, messages_used, mean_relative_error = manifest_world(build_func, key_funcs, attr_funcs, raw_queries, args.n_switches, n_packets)
                results += ((build_name, n_packets, n_queries, memory_used, messages_used, mean_relative_error),)
    pdb.set_trace()
    dummy = 0 


