import pickle 
import pdb

import matplotlib.pyplot as plt 
import numpy as np 

with open('results.pickle', 'rb') as f:
         results = pickle.load(f)

def get_spec(build_name:str, q_name:str, idxs:tuple, results:tuple) -> np.ndarray: 
    spec = [] 
    for result in results: 
        build, q, *rest = result
        if (build == build_name) and (q == q_name): 
            spec.append([result[idxs[0]], result[idxs[1]]])
    return np.array(spec)

query_set = {'set_1', 'set_2', 'set_3', 'set_4'}
fig, axs = plt.subplots(nrows=2)
axs[0].set_title('Number of packets versus memory') 
axs[0].set_xlabel('Number of packets') 
axs[0].set_ylabel('Memory') 
axs[1].set_title('Number of packets versus messages sent') 
axs[1].set_xlabel('Number of packets') 
axs[1].set_ylabel('Number of messages') 
build_colors = ['r', 'b', 'g', 'y']

for i, build in enumerate(['PMP', 'PPMP']): 
    col = build_colors[i]
    for query in query_set: 
        pkts_v_memory = get_spec(build, query, (2, 5), results)
        pkts_v_messages = get_spec(build, query, (2, 4), results) 
        axs[0].plot(pkts_v_memory[:, 0], pkts_v_memory[:, 1], c=col)
        axs[1].plot(pkts_v_messages[:, 0], pkts_v_messages[:, 1], c=col)

for j, build in enumerate(['Standalone', 'ZeroError']): 
    col = build_colors[j+2]
    for query in query_set: 
        pkts_v_messages = get_spec(build, query, (2, 4), results)
        axs[1].plot(pkts_v_messages[:, 0], pkts_v_messages[:, 1], c=col)
plt.show() 







