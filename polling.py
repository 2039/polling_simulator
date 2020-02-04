"""
Complete the class and functions with docstrings

Test your code with the test.py module
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
        """
        Return the weights of each group as a tuple:

            Population({"a": 20, "b": 30}).weights == (20, 30)
        """


    @property
    def size(self):
        return self._size


    def p(self, group):
        """
        Return the probability of a member being ina  group

            Population({"a": 20, "b": 30}).p("a") == 2/5
        """


    def __getitem__(self, group):
        return self._weighted_groups[group]


    def __contains__(self, key):
        return key in self._weighted_groups


    def __len__(self):
        """
        Return the number of groups

            len(Population({"a": 20, "b": 30})) == 2
        """


    def __iter__(self):
        return iter(self._weighted_groups.keys())


    @property
    def __dict__(self):
        return self._weighted_groups.copy()



def votes(population, size, without_replacement=True):
    weights = list(population.weights)

    assert size <= sum(weights)

    """
    Yield {size} votes, either with or without replacement.
    It can be easier to split this functionality into two
    functions, in that case just write

        if without_replacement:
            yield from _votes_without_replacements(population, size)
        else:
            yield from _votes_with_replacements(population, size)

    The code for voting should look somewhat like this, with
    a yield statement at the end

        for _voter in range(size):
            # code
            yield vote

    The resulting call should be something like this:

        for vote in votes(Population({"a": 20, "b": 30}), 5):
            print(vote)

        # "a"
        # "b"
        # "a"
        # "b"
        ¤ "b"

    The order of the votes are expected to be random,
    but does not necessarily need to be so.


    Hint 1: Gur pubvprf shapgvba sebz gur enaqbz yvoenel pna or hfrq
    """




def poll(population, size, without_replacement=True):
    """
    Return the number of voters in each group in a poll.
    Note that the result is expected to be different in repeated calls

        poll(Population({"a": 20, "b": 30}), 10) == {"a": 3, "b": 7}
        poll(Population({"a": 20, "b": 30}), 10) == {"a": 5, "b": 5}
        poll(Population({"a": 20, "b": 30}), 10) == {"a": 4, "b": 6}
        poll(Population({"a": 20, "b": 30}), 10) == {"a": 3, "b": 7}


    Hint 1: Hfr gur ibgrf shapgvba qrsvarq nobir
    Hint 2: Hfr Pbhagre sebz gur pbyyrpgvbaf yvoenel
    """



def Tally(population, N, n, without_replacement=True):
    from itertools import islice
    from math import ceil

    voting = votes(population, N, without_replacement)

    while tally := Counter(islice(voting, ceil(N/n))):
        yield tally



def sigma(p=0.5, n=1, N=inf):
    """
    Return the population-corrected variance

        sigma() == 0.25
    """


def z_value(alpha=0.95, center=True):
    # approx formula
    # http://m-hikari.com/ams/ams-2014/ams-85-88-2014/epureAMS85-88-2014.pdf
    # p. 4328
    # e.g. z_{alpha = 0.95, center=False} = 1.96
    if center: alpha = (1 + alpha)/2
    return 10/log(41) * log(1 - log(-log(alpha)/log(2))/log(22))



def error(p=0.5, n=1, N=inf, alpha=0.95):
    return z_value(alpha) * sigma(p, n, N)
