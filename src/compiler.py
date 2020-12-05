from typing import Union 

import numpy as np 

from constants import WORD_SIZE
from query import Query

def _max_coupons(query : tuple) -> tuple: 
    feasible_probs, max_coupons = [], []
    for j in range(WORD_SIZE): 
        prob = 2**-j
        if query.num_coupons * prob <= query.mean_coupons: 
            m = min(WORD_SIZE, query.mean_coupons/prob) 
            if m < 1: 
                break 
            else: 
                feasible_probs.append(prob); max_coupons.append(m)
    return feasible_probs, max_coupons

def _get_reasonable_configs(feasible_probs : list, max_coupons : list) -> list: 
    raise(NotImplementedError)

if __name__ == "__main__":
    pass 
    