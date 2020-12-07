import logging 
from typing import Union 

import numpy as np 

from constants import WORD_SIZE
from query import RawQuery

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING) 
file_handler = logging.FileHandler('logs/compiler.log') 
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

def expected_draws(m, p, n): 
    draws = 0 
    for j in range(n): 
        draws += 1/(p*(m-j))
    return draws

def _get_reasonable_configs(feasible_probs : list, max_coupons : list, threshold: int) -> list: 
    configs = () 
    for p_q, m_q in zip(feasible_probs, max_coupons): 
        for m in range(1, int(m_q)): 
            for n in range(1, m+1): 
                assert 1 <= n and n <= m and m <= m_q, "somethings not right..." 
                e_draws = expected_draws(m, p_q, n)
                if 0.95 * threshold < e_draws < 1.05 * threshold: # TODO: relax this if no reasonable config is found
                    configs += ((m, p_q, n),)
    return configs

def compiler(raw_query: RawQuery) -> tuple: 
    feasible_probs, max_coupons = _max_coupons(raw_query) 
    configs = _get_reasonable_configs(feasible_probs, max_coupons, raw_query.threshold) # TODO simulated table 
    (m, p, n) = configs[0]
    return (m, p, n) 

if __name__=="__main__": 
    query = RawQuery(1, 1, 33612, 0.13332, 'random') 
    config = compiler(query)

