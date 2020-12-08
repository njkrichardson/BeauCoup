def absolute_error(n_distinct : int, threshold : int) -> int: 
    return abs(n_distinct - threshold)

def relative_error(n_distinct : int, threshold : int) -> float: 
    return absolute_error(n_distinct, threshold)/threshold
