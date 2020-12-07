import random 

import pytest

from constants import WORD_SIZE
from compiler import compiler 
from query import RawQuery

LEVEL = 2 

def run_compiler(t_range: tuple = (int(10e2), int(10e4))) -> tuple: 
    threshold, mean_activation = random.randint(*t_range), random.random()
    (m, p, n) = compiler(RawQuery(1, 1, threshold, mean_activation, 'random_query'))
    return (m, p, n, threshold, mean_activation) 
    
def test_memory(): 
    for _ in range(int(10**LEVEL)):
        m, *_ = run_compiler() 
        assert m <= WORD_SIZE

def test_mean_activation(): 
    for _ in range(int(10**LEVEL)): 
        m, p, _, _, mean_activation = run_compiler() 
        assert m * p < mean_activation
