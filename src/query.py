from collections import namedtuple

Query = namedtuple('Query', ['attribute_func', 'key_func', 'threshold', 'num_coupons', 'mean_coupons'])
