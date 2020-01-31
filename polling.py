"""
[ ] Add unittest
[ ] Make abstract methods (?)
[o] Add argparse
"""

import argparse
from collections import Counter
from random import choices, sample, seed
from math import sqrt
from matplotlib import pyplot as plt

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", default=[], nargs="*", help="Run given tests.")
parser.add_argument("-s", "--seed", default=0, type=int, help="Set seed.")

options = parser.parse_args()

# Set seed
seed(options.seed)


class Population:
    def __init__(self, weighted_groups):
        self.groups = tuple(weighted_groups.keys())
        self.weights = tuple(weighted_groups.values())
        self.group_index = {group : i for i, group in enumerate(self.groups)}

    def __getitem__(self, group):
        return self.weights[self.group_index[group]]



def _poll_without_replacement(population, size):
    assert size <= sum(population.weights)

    weights = list(population.weights)


    # naive
    voters = [g for g in population.groups for _p in range(population[g])]

    return Counter(sample(voters, k=size))

    # def votes():
    #     for _person in range(size):
    #         vote = choices(population.groups, weights)[0]
    #         # update weights; remove voter from valid voters
    #         weights[population.group_index[vote]] -= 1
    #         yield vote

    # return Counter(votes())



def _poll_with_replacement(population, size):
    assert size <= sum(population.weights)

    weights = list(population.weights)

    # naive
    return Counter(choices(population.groups, weights, k=size))


    # def votes():
    #     for _person in range(size):
    #         vote = choices(population.groups, weights)[0]
    #         yield vote

    # return Counter(votes())



def poll(population, size, *, without_replacement=False):
    if without_replacement:
        return _poll_without_replacement(population, size)
    else:
        return _poll_with_replacement(population, size)



def sigma(group_size, population_size, *, fpc=False, exact=False):
    n, N = group_size, population_size

    p = n / N if exact else 0.5

    sigma = sqrt(p * (1-p) / n) * (sqrt((N-n)/(N-1)) if fpc else 1)

    return sigma



population = Population({
    "a" : 100,
    "b" : 600,
    "c" : 999,
})

if __name__ == "__main__":
    result = poll(population, sum(population.weights), without_replacement=False)

    print(result)

    s = sigma(result["a"], sum(population.weights))

    print(s)

    for test in options.test:
        # todo
        print(test)

# ===

def error(self, alpha):
    self._assert_has_polled()

    # approx formula
    # http://m-hikari.com/ams/ams-2014/ams-85-88-2014/epureAMS85-88-2014.pdf
    # e.g. z_{alpha = 0.95} = 2
    z_alpha = 10/math.log(41) * math.log(
        1 - math.log(-math.log(alpha)/math.log(2))/math.log(22)
    )

    return self._polls[-1].sigma * z_alpha * 100

# ===

from scipy.stats import binom, hypergeom, norm

binomial_pmf = binom.pmf
hypergeometric_pmf = hypergeom.pmf
normal_pdf = norm.pdf

# ===

def foo():
    for rect, change in zip(rects, changes):
        x = rect.get_x() + rect.get_width()/2
        y = rect.get_height()

        ax.text(x, y, f"{y:.1f}", ha='center', va='bottom')

        if _changes:
            cs = '▲' if change > 0 else ('▼' if change < 0 else '■')
            cc = 'g' if change > 0 else ('r' if change < 0 else 'k')

            ax.text(x, y, f"{cs} {change:.1f}", ha="center", va="top", color=cc)

# ===

p = 1/3 # 16 / 100
n = 5 # 1_000
N = 30 # 5_000_000

N_s = 1000

X = list(range(n+1))
X_s = list(range(N_s+1))
X_p = [x/n for x in X]
X_sp = [x/(N_s+1) for x in X_s]

sigma = math.sqrt(p * (1-p) / n)
sigma_fpc = sigma * math.sqrt((N - n)/(N-1))

sigma_hat = math.sqrt(1/2 * (1-1/2) / n)

Y = [binomial_pmf(x, n, p) for x in X]
Y_fpc = [hypergeometric_pmf(x, N, int(N*p), n) for x in X]
Y_CLT = [normal_pdf(x, p, sigma)/n for x in X_sp]
Y_CLT_fpc = [normal_pdf(x, p, sigma_fpc)/n for x in X_sp]
Y_CLT_worst = [normal_pdf(x, p, sigma_hat)/n for x in X_sp]
