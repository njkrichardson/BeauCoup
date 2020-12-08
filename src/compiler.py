import logging 
import pdb
from typing import Union 

import numpy as np 

from constants import WORD_SIZE
from query import Query, RawQuery

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING) 
try: 
    file_handler = logging.FileHandler('logs/compiler.log') 
except: 
    file_handler = logging.FileHandler('src/logs/compiler.log') 
logger.addHandler(file_handler) 

def _max_coupons(query : tuple) -> tuple: 
    feasible_probs, max_coupons = [], []
    for j in range(1, WORD_SIZE): 
        prob = 2**-j
        m = min(WORD_SIZE, query.mean_activation/prob) 
        logger.debug(f"Integer multiple j = {j}\tprobability: 2^-{j}\tm (total coupon number): {m}") 
        if m >= 1: 
            feasible_probs.append(prob); max_coupons.append(m)
        else: 
            logging.debug(f"Value of m = {m} < 1... stopping...") 

    return feasible_probs, max_coupons

def _expected_draws(m, p, n): 
    draws = 0 
    for j in range(n): 
        draws += m/(p*(m-j))
    return draws

def _variance(m, p, n):
    var = 0
    for j in range(n):
        var += m * (1 - p + j/m)/(m-j)/(m-j)/p/p
    return var

def _get_reasonable_configs(feasible_probs : list, max_coupons : list, threshold: int) -> list: 
    configs = () 
    for p_q, m_q in zip(feasible_probs, max_coupons): 
        for m in range(1, int(m_q)): 
            for n in range(1, m+1): 
                assert 1 <= n and n <= m and m <= m_q, "somethings not right..." 
                e_draws = _expected_draws(m, p_q, n)
                if 0.95 * threshold < e_draws < 1.05 * threshold: # TODO: relax this if no reasonable config is found
                    log_error = np.abs(np.log(e_draws)-np.log(threshold))
                    var = _variance(m, p_q, n)
                    configs += ((log_error, (m, p_q, n), var),)
    return configs

def compiler(raw_query: RawQuery) -> tuple: 
    feasible_probs, max_coupons = _max_coupons(raw_query) 
    configs = _get_reasonable_configs(feasible_probs, max_coupons, raw_query.threshold) 
    configs = sorted(configs, key=lambda x: x[2])
    # print(configs)
    try: 
        print(configs[0])
    except: 
        pdb.set_trace() 
    print(np.sqrt(configs[0][2]))
    (m, p, n) = configs[0][1]
    return (m, p, n) 

def compile_queries(raw_queries: list) -> list:
    queries = []
    for rq in raw_queries:
        m, p, n = compiler(rq)
        queries += [Query(p, m, n, rq),]
    return queries

