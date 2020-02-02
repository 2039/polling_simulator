"""
"""

import argparse
import unittest
from random import seed

from polling import poll, votes, Population, sigma
from collections import Counter

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", default=[], type=int, nargs="*", help="Run given tests.")
parser.add_argument("-s", "--seed", default=0, type=int, help="Set seed.")

options = parser.parse_args()


# ===

class Test_Voting(unittest.TestCase):
    def setUp(self):
        seed(options.seed)
        self.votes = votes


    def test_empty(self):
        population = Population(dict())

        vote_count = sum(1 for _vote in self.votes(population, 0))
        self.assertEqual(vote_count, 0)


    def test_sample(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        for vote in self.votes(population, 5):
            self.assertIn(vote, population.groups)



class Test_With_Replacement(unittest.TestCase):
    def setUp(self):
        seed(options.seed)
        self.poll = poll


    def test_empty(self):
        population = Population(dict())
        self.assertEqual(self.poll(population, 0), Counter())

    def test_poll_N(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        for N in (3, 7, 31):
            polling = self.poll(population, N)
            votes = sum(polling.values())

            self.assertEqual(votes, N)


    def test_uniqueness(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        poll1 = self.poll(population, 15)
        poll2 = self.poll(population, 15)

        # Probabilistic test
        self.assertNotEqual(poll1, poll2)


    def test_poll_all(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        N = sum(population.weights)

        polling = self.poll(population, N)

        # Probabilistic test
        self.assertNotEqual(polling, Counter(vars(population)()))
        self.assertEqual(polling.keys(), vars(population)().keys())



class Test_Without_Replacement(unittest.TestCase):
    def setUp(self):
        seed(options.seed)

        from functools import partial
        self.poll = partial(poll, without_replacement=True)


    def test_empty(self):
        population = Population(dict())

        self.assertEqual(self.poll(population, 0), Counter())


    def test_poll_N(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        for N in (3, 7, 31):
            polling = self.poll(population, N)
            votes = sum(polling.values())

            self.assertEqual(votes, N)


    def test_uniqueness(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        poll1 = self.poll(population, 15)
        poll2 = self.poll(population, 15)

        # Probabilistic test
        self.assertNotEqual(poll1, poll2)


    def test_poll_all(self):
        population = Population({
            "a" : 10,
            "b" : 20,
            "c" : 30,
        })

        N = sum(population.weights)

        polling = poll(population, N, without_replacement=True)
        self.assertEqual(polling, Counter(vars(population)()))



class Test_Error(unittest.TestCase):
    def test_simple(self):
        args_result = {
            (50, 100) : 0.07071067811865475,
            (5, 10)   : 0.22360679774997896,
            (1, 2)    : 0.5,
            (10, 10)  : 0.15811388300841897,
            (10, 100) : 0.15811388300841897,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args), result)

    def test_fpc(self):
        args_result = {
            (50, 100) : 0.050251890762960605,
            (5, 10)   : 0.16666666666666666,
            (1, 2)    : 0.5,
            (10, 10)  : 0.0,
            (10, 100) : 0.15075567228888181,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args, fpc=True), result)

    def test_exact(self):
        args_result = {
            (50, 100) : 0.07071067811865475,
            (5, 10)   : 0.22360679774997896,
            (1, 2)    : 0.5,
            (10, 10)  : 0.0,
            (10, 100) : 0.09486832980505139,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args, exact=True), result)

    def test_fpc_and_exact(self):
        args_result = {
            (50, 100) : 0.050251890762960605,
            (5, 10)   : 0.16666666666666666,
            (1, 2)    : 0.5,
            (10, 10)  : 0.0,
            (10, 100) : 0.09045340337332909,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args, fpc=True, exact=True), result)



tests = [
    Test_Voting,
    Test_With_Replacement,
    Test_Without_Replacement,
    Test_Error,
]
tests = [tests[t-1] for t in options.test]

runner = unittest.TextTestRunner()

for test in tests:
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test)
    runner.run(test_suite)
