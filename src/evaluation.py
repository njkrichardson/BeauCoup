from math import abs 

import numpy as np 
from tqdm import tqdm

def simulate_packet_flow(): 
    raise(NotImplementedError)

def absolute_error(n_distinct : int, threshold : int) -> int: 
    return abs(n_distinct - threshold)

def relative_error(n_distinct : int, threshold : int) -> float: 
    return absolute_error/threshold

def mean_relative_error(n_distinct : int, threshold : int, **kwargs) -> float: 
    errors = [] 
    for _ in tqdm(range(kwargs.get('iters', int(1e3))), disable=kwargs.get('silent', False)): 
        n_distinct = simulate_packet_flow()
        errors.append(relative_error(n_distinct, threshold))
    if kwargs.get('return_all', False): 
        return np.array(errors) 
    else: 
        return np.array(errors).mean 
