from collections import namedtuple
from enum import Enum 
import warnings 

import numpy as np 
import matplotlib
import matplotlib.pyplot as plt

Domain = namedtuple('Domain', ['low', 'high', 'resolution']) 

def contour_plot(f : callable, domains : tuple, display : bool = True, **kwargs): 
    # TODO: assumes f takes a single vector valued input 
    x_dom, y_dom = domains
    levels = kwargs.get('levels', 5)
    x, y = np.meshgrid(np.linspace(x_dom.low, x_dom.high, x_dom.resolution), np.linspace(y_dom.low, y_dom.high, y_dom.resolution)) 
    try: 
        z = f(np.array([x, y])) 
    except: 
        z = np.empty((x_dom.resolution, y_dom.resolution))
        for i in range(x_dom.resolution): 
            for j in range(y_dom.resolution): 
                z[i, j] = f(np.array([x[i, j], y[i, j]]))
    fig = plt.figure() 
    plt.contour(x, y, z, levels, cmap='gray')
    if display is True:  
        plt.show() 
    else: 
        return fig 

def setup_tex_backend(return_state : bool = True): 
    try: 
        matplotlib.rcParams['text.usetex'] = True
        return True if return_state is True else None 
    except: 
        warnings.warn('Matplotlib tex backend not configured')
        return False if return_state is True else None 
