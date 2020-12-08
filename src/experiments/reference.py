import argparse 
from functools import partial 
import collections
import logging 
import random

from compiler import compile_queries
from packet import Packet, parse_packet_stream
from query import Query, RawQuery, convert_queries, Conf, default_query_configs
from utils import phash, count, flip_coin
from simulate import manifest_world, build_zeroerror 

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
file_handler = logging.FileHandler('logs/experiments/zero_error.log')
logger.addHandler(file_handler)

parser = argparse.ArgumentParser(description='A simple (and admittedly inefficient) but correct configuration to be used as a reference implementation.')
parser.add_argument('--query_class', type=str, default='all', help='which class of query configurations to use')
parser.add_argument('--n_switches', type=int, default=3, help='number of switches to simulate')
parser.add_argument('--n_packets', type=int, default=int(10e4), help='number of packets to simulate')
args = parser.parse_args()

if __name__ == "__main__":
    key_funcs, attr_funcs = default_query_configs(args.query_class)

    # TODO: randomize this 
    raw_queries = [
            RawQuery(0, 1, 100, 0.1, 'Test'),
            ]

    manifest_world(partial(build_zeroerror, key_funcs, attr_funcs, raw_queries), args.n_switches, args.n_packets) 
