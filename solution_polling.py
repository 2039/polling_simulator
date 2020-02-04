"""
Ex 1: Finish the Population.p(group) method.
It should return the probability of a random sample being from that group.
"""

from collections import Counter
from random import choices, sample
from math import sqrt, log, inf



class Population:
    def __init__(self, weighted_groups):
        self._weighted_groups = weighted_groups
        self.group_index = {group : i for i, group in enumerate(self.groups)}
        self._size = sum(self.weights)


    @property
    def groups(self):
        return tuple(self._weighted_groups.keys())


    @property
    def weights(self):
        return tuple(self._weighted_groups.values())


    @property
    def size(self):
        return self._size


    def p(self, group):
        return self[group] / sum(self.weights)


    def __getitem__(self, group):
        return self._weighted_groups[group]


    def __contains__(self, key):
        return key in self._weighted_groups


    def __len__(self):
        return len(self.groups)


    def __iter__(self):
        return iter(self._weighted_groups.keys())

    @property
    def __dict__(self):
        return self._weighted_groups.copy()



def votes(population, size, without_replacement=True):
    weights = list(population.weights)

    assert size <= sum(weights)

    for _person in range(size):
        vote = choices(population.groups, weights)[0]
        if without_replacement:
            # update weights; remove voter from valid voters
            weights[population.group_index[vote]] -= 1
        yield vote



def poll(population, size, without_replacement=True):
    return Counter(votes(population, size, without_replacement=without_replacement))



def Tally(population, N, n, without_replacement=True):
    from itertools import islice
    from math import ceil

    def take(it, n): return islice(it, n)

    voting = votes(population, N, without_replacement=without_replacement)

    while tally := Counter(take(voting, ceil(N/n))):
        yield tally



def sigma(p=0.5, n=1, N=inf):
    return sqrt(p * (1-p) / n) * sqrt(1 - (n-1)/(N-1))



def z_value(alpha=0.95, center=True):
    # approx formula
    # http://m-hikari.com/ams/ams-2014/ams-85-88-2014/epureAMS85-88-2014.pdf
    # p. 4328
    # e.g. z_{alpha = 0.95, center=False} = 1.96
    if center: alpha = (1 + alpha)/2
    return 10/log(41) * log(1 - log(-log(alpha)/log(2))/log(22))



def error(p=0.5, n=1, N=inf, alpha=0.95):
    """
    The approximate error of a binomial distribution as a limit to the bell.
    This approximation has several inaccuracies, including, but not limited to:
    * No continuity correction (+ 0.5/n)
    * Biased estimator (also known as wald method)
    * Unknown sigma should imply the use of the t-distribution,
        instead of the bell distribution, but given that the assumption
        to use the bell distribution as a limiting distribution, the sample
        size is already large enough to justify the use of the z_value.
    """
    return z_value(alpha) * sigma(p, n, N)
