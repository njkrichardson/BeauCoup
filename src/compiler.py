import logging 
from typing import Union 

import numpy as np 

from constants import WORD_SIZE
from query import Query

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 
file_handler = logging.FileHandler('compiler.log') 
logger.addHandler(file_handler) 

def _max_coupons(query : tuple, mean_activation) -> tuple: 
    feasible_probs, max_coupons = [], []
    for j in range(1, WORD_SIZE): 
        prob = 2**-j
        m = min(WORD_SIZE, mean_activation/prob) 
        logger.debug(f"Integer multiple j = {j}\tprobability: 2^-{j}\tm (total coupon number): {m}") 
        if m < 1: 
            logging.debug(f"Value of m = {m} < 1... stopping...") 
            break 
        else: 
            feasible_probs.append(prob); max_coupons.append(m)
    return feasible_probs, max_coupons

def expected_draws(m, p, n): 
    draws = 0 
    for j in range(n): 
        draws += 1/(p*(m-j))
    return draws

def _get_reasonable_configs(feasible_probs : list, max_coupons : list, threshold) -> list: 
    configs = () 
    for p_q, m_q in zip(feasible_probs, max_coupons): 
        for m in range(1, int(m_q)): 
            for n in range(1, m+1): 
                assert 1 <= n and n <= m and m <= m_q, "somethings not right..." 
                e_draws = expected_draws(m, p_q, n)
                if 0.95 * threshold < e_draws < 1.05 * threshold: # TODO: relax this if no reasonable config is found
                    configs += ((m, p_q, n),)
    return configs


def compiler(query, threshold: int, mean_activation: float): 
    feasible_probs, max_coupons = _max_coupons(query, mean_activation) 
    configs = _get_reasonable_configs(feasible_probs, max_coupons, threshold) 
    # TODO: simulation table; currently just takes first element 
    (m, p, n) = configs[0]
    compiler_constraints(m, p, n, mean_activation)
    return (m, p, n) 

def compiler_constraints(m, p, n, mean_activation: float): 
    assert m <= WORD_SIZE, f"number of coupons exceeds current word size of {WORD_SIZE}"
    assert m * p < mean_activation, f"number of coupons {m} times probability of collection {p} = {m} x {p} = {m*p} which exceeds the mean activation {mean_activation}"
    logging.info('All constraints satisfied') 

