## BeauCoup: Network Analysis in Resource Constrained Settings 

This repository contains a reimplementation of the BeauCoup network administration system formulated by Chen et al [1]. BeauCoup is comprised of an algorithmic component inspired by the coupon collector's problem in probability theory [2], and a compiler for parameter configuration to optimize system accuracy. 

### Installation 

One can clone the repository over secure shell or https. To install the required dependencies, navigate to the project root and run 

```python 
pip install . 
``` 

---

#### References 

[1] Chen, X., Landau-Feibish, S., Braverman, M., & Rexford, J. (2020, July). BeauCoup: Answering Many Network Traffic Queries, One Memory Update at a Time. In Proceedings of the Annual conference of the ACM Special Interest Group on Data Communication on the applications, technologies, architectures, and protocols for computer communication (pp. 226-239). ([ACM Reference](https://www.cs.princeton.edu/~jrex/papers/beaucoup20.pdf))

[2] Boneh, A., & Hofri, M. (1997). The coupon-collector problem revisited—a survey of engineering problems and computational methods. Stochastic Models, 13(1), 39-66.