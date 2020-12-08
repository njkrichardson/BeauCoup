import argparse 
from functools import partial 
import collections
import logging 
import random

from packet import Packet, parse_packet_stream
from query import Query, RawQuery, convert_queries, Conf, default_query_configs
from utils import phash, count, flip_coin
from simulate import manifest_world, build_functions

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
file_handler = logging.FileHandler('logs/experiments/beaucoup_experiment.log')
logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description='A standalone switch coupon collection problem; corresponds to the BeauCoup problem.') 
parser.add_argument('--system_type', type=str, default='Standalone',
        choices=build_functions.keys(), help='which system of servers and switches to simulate')
parser.add_argument('--query_class', type=str, default='all', help='which class of query configurations to use')
parser.add_argument('--n_switches', type=int, default=1, help='number of switches to simulate')
parser.add_argument('--n_packets', type=int, default=int(10e4), help='number of packets to simulate')
args = parser.parse_args()

if __name__ == "__main__":
    key_funcs, attr_funcs = default_query_configs(args.query_class)
    build_func = build_functions[args.system_type]

    # TODO: randomize this 
    raw_queries = [
            RawQuery(0, 1, 100, 0.1, 'Test'),
            ]

    manifest_world(partial(build_func, key_funcs, attr_funcs, raw_queries), args.n_switches, args.n_packets)
