import argparse 
import collections
from functools import partial 
import logging 
import random

from compiler import compile_queries
from packet import Packet, parse_packet_stream
from query import Query, RawQuery, convert_queries, Conf, default_query_configs
from utils import phash, count, flip_coin
from simulate import build_pmp, manifest_world

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
file_handler = logging.FileHandler('logs/pmp_experiment.log')
logger.addHandler(file_handler)

parser = argparse.ArgumentParser() 
parser.add_argument('--query_class', type=str, default='all')
parser.add_argument('--n_switches', type=int, default=3)
parser.add_argument('--n_packets', type=int, default=int(10e4))
args = parser.parse_args()

if __name__ == "__main__":
    key_funcs, attr_funcs = default_query_configs(args.query_class)

    # TODO: randomize this 
    raw_queries = [
            RawQuery(0, 1, 100, 0.1, 'Test'),
            ]
    manifest_world(partial(build_pmp, key_funcs, attr_funcs, raw_queries), args.n_switches, args.n_packets) 
