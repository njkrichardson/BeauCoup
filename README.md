## BeauCoup: Network Analysis in Resource Constrained Settings 

This repository contains a logical clone of the BeauCoup network administration system formulated by Chen et al [1] with our own extensions into the multi-switch coupon collection setting. BeauCoup is comprised of an algorithmic component inspired by the coupon collector's problem in probability theory [2], and a compiler for parameter configuration to optimize system accuracy. 

### Installation 

One can clone the repository over secure shell or https. To install the required dependencies, navigate to the project root and run 

```python 
pip install . 
``` 

---

### Replication 

Check out the experiments in `src/experiments` to replicate the results provided in our report. Each simulation has parameters which can be modulated to change the simulation behavior (e.g., the number of packets in the simulation word). Use the `-h` flag to get information on how these parameters work:

```bash
>> python src/experiments/beaucoup.py -h`
>> 
usage: beaucoup.py [-h] [--query_class QUERY_CLASS] [--n_switches N_SWITCHES]
                   [--n_packets N_PACKETS]

A standalone switch coupon collection problem; corresponds to the BeauCoup
problem.

optional arguments:
  -h, --help            show this help message and exit
  --query_class QUERY_CLASS
                        which class of query configurations to use
  --n_switches N_SWITCHES
                        number of switches to simulate
  --n_packets N_PACKETS
                        number of packets to simulate
```

Note that changing the psuedo-random number generator seed in `src/constants.py` would cause the timelines you simulate proceed similarly though not identically to ours. 

#### References 

[1] Chen, X., Landau-Feibish, S., Braverman, M., & Rexford, J. (2020, July). BeauCoup: Answering Many Network Traffic Queries, One Memory Update at a Time. In Proceedings of the Annual conference of the ACM Special Interest Group on Data Communication on the applications, technologies, architectures, and protocols for computer communication (pp. 226-239). ([ACM Reference](https://www.cs.princeton.edu/~jrex/papers/beaucoup20.pdf))

[2] Boneh, A., & Hofri, M. (1997). The coupon-collector problem revisited—a survey of engineering problems and computational methods. Stochastic Models, 13(1), 39-66.
