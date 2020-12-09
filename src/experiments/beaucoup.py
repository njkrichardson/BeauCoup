import argparse 
import collections
import logging 
import random
import pdb 
import pickle 

import numpy as np 
import matplotlib.pyplot as plt 
from tqdm import tqdm 

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
parser.add_argument('--query_class', type=str, default='hack', help='which class of query configurations to use (e.g., \'mix\', \'all\', \'spreader\')')
parser.add_argument('--n_switches', type=int, default=3, help='number of switches to simulate (a positive integer)')
parser.add_argument('--n_packets', type=int, default=int(10e4), help='number of packets to simulate (a positive integer)')
parser.add_argument('--system_type', type=str, default='Standalone', choices=build_functions.keys(), help='which system of servers and switches to simulate')
parser.add_argument('--n_queries', type=int, default=2, help='number of queries to use') 
args = parser.parse_args()

if __name__ == "__main__":
    query_set = {'set_1', 'set_2', 'set_3', 'set_4'}

    results = () 
    n_packet_range = [int(1e4), int(3e4), int(5e4)]
    n_queries_range = [2] 
    for build_name, build_func in build_functions.items(): 
        for q_class in tqdm(query_set): 
            for n_packets in n_packet_range: 
                for n_queries in n_queries_range: 
                    key_funcs, attr_funcs = default_query_configs(q_class, n_queries)
                    raw_queries = [] 
                    for i in range(n_queries): 
                        t_range = (50, 100)
                        m_activation = random.randint(70, 80)/100
                        raw_queries.append(RawQuery(i, i, random.randint(*t_range), m_activation, f'query_{i}'))

                    memory_used, messages_used, mean_relative_error = manifest_world(build_func, key_funcs, attr_funcs, raw_queries, args.n_switches, n_packets)
                    results += ((build_name, q_class,  n_packets, n_queries, memory_used, messages_used, mean_relative_error),)

    with open('results.pickle', 'wb') as f:
            pickle.dump(results, f)

    # visuals 
    colormap = dict(set_1='r', set_2='b', set_3='y', set_4='g')
    n_sub = 2
    fig, axs = plt.subplots(nrows=n_sub)
    axs[0].set_title('Number of packets versus memory usage') 
    axs[1].set_title('Number of packets versus number of messages') 

    for q_class_ref in query_set: 
        pmp_packets_vs_messages = [] 
        pmp_packets_vs_memory = [] 

        ppmp_packets_vs_messages = [] 
        ppmp_packets_vs_memory = [] 

        standalone_packets_vs_messages = [] 
        zeroerror_packets_vs_messages = []

        for result in results: 
            name, q_class, num_packets, num_queries, memory_usage, num_messages, err = result
            if name is 'PMP' and q_class is q_class_ref: 
                pmp_packets_vs_messages.append([num_packets, num_messages]) 
                pmp_packets_vs_memory.append([num_packets, memory_usage])
            elif name is 'PPMP' and q_class is q_class_ref: 
                ppmp_packets_vs_messages.append([num_packets, num_messages]) 
                ppmp_packets_vs_memory.append([num_packets, memory_usage])
            elif name is 'Standalone' and q_class is q_class_ref: 
                standalone_packets_vs_messages.append([num_packets, num_messages])
            elif name is 'ZeroError' and q_class is q_class_ref: 
                zeroerror_packets_vs_messages.append([num_packets, num_messages])
            else: 
                continue
        # pdb.set_trace() 

        pmp_packets_vs_messages = np.array(pmp_packets_vs_messages)
        pmp_packets_vs_memory = np.array(pmp_packets_vs_memory)

        ppmp_packets_vs_messages = np.array(ppmp_packets_vs_messages)
        ppmp_packets_vs_memory = np.array(ppmp_packets_vs_memory)

        standalone_packets_vs_messages = np.array(standalone_packets_vs_messages)
        zeroerror_packets_vs_messages = np.array(zeroerror_packets_vs_messages)

        axs[0].scatter(pmp_packets_vs_memory[:, 0], pmp_packets_vs_memory[:, 1], label='pmp' + q_class_ref)
        axs[0].scatter(ppmp_packets_vs_memory[:, 0], ppmp_packets_vs_memory[:, 1], label='ppmp' + q_class_ref)

        axs[1].scatter(pmp_packets_vs_messages[:, 0], pmp_packets_vs_messages[:, 1], label='pmp' + q_class_ref)
        axs[1].scatter(ppmp_packets_vs_messages[:, 0], ppmp_packets_vs_messages[:, 1], label='ppmp' + q_class_ref)
        axs[1].scatter(standalone_packets_vs_messages[:, 0], standalone_packets_vs_messages[:, 1], label='standalone' + q_class_ref)
        axs[1].scatter(zeroerror_packets_vs_messages[:, 0], zeroerror_packets_vs_messages[:, 1], label='zeroerror' + q_class_ref)

    plt.legend()
    plt.show() 

        
        


