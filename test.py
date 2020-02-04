"""
To run this program, write in terminal:
>>> py test.py --test <test numbers>
i.e to run the first three tests:
>>> py test.py --test 1 2 3
"""

import argparse
import unittest
from random import seed

from polling import poll, votes, Population, Tally, sigma
from collections import Counter

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", default=[], type=int, nargs="*", help="Run given tests.")
parser.add_argument("-s", "--seed", default=0, type=int, help="Set seed.")

options = parser.parse_args()


# ===

class Test_Population(unittest.TestCase):
    def setUp(self):
        self.pop_dict = {
            "a" : 10,
            "b" : 20,
            "c" : 30,
        }

        self.empty = Population({})
        self.pop = Population(self.pop_dict)



    def test_weights(self):
        self.assertEqual(self.empty.weights, ())
        self.assertEqual(self.pop.weights, tuple(self.pop_dict.values()))


    def test_groups(self):
        self.assertEqual(self.empty.groups, ())
        self.assertEqual(self.pop.groups, tuple(self.pop_dict.keys()))


    def test_size(self):
        self.assertEqual(self.empty.size, 0)
        self.assertEqual(self.pop.size, 60)


    def test_len(self):
        self.assertEqual(len(self.empty), 0)
        self.assertEqual(len(self.pop), 3)


    def test_vars(self):
        self.assertEqual(vars(self.empty), {})
        self.assertEqual(vars(self.pop), self.pop_dict)


    def test_getter(self):
        self.assertEqual(self.pop["a"], 10)
        self.assertEqual(self.pop["b"], 20)
        self.assertEqual(self.pop["c"], 30)


    def test_p(self):
        self.assertEqual(self.pop.p("a"), 10/60)
        self.assertEqual(self.pop.p("b"), 20/60)
        self.assertEqual(self.pop.p("c"), 30/60)


    def test_iterable(self):
        for g1, g2 in zip(self.pop, self.pop_dict):
            self.assertEqual(g1, g2)


    def test_contains(self):
        for group in self.pop_dict:
            group in self.pop


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



class Test_Tallying(unittest.TestCase):
    def setUp(self):
        seed(options.seed)
        self.Tally = Tally


    def test_empty(self):
        population = Population(dict())

        tally_count = sum(1 for _tally in self.Tally(population, 0, 1))
        self.assertEqual(tally_count, 0)


    def test_sample(self):
        population = Population({
            "a" : 20,
            "b" : 40,
            "c" : 60,
        })

        N, n = 74, 3

        tallies = list(self.Tally(population, N, n))

        counts = [sum(tally.values()) for tally in tallies]

        self.assertEqual(counts, [25, 25, 24])
        self.assertEqual(len(tallies), n)




class Test_Poll_With_Replacement(unittest.TestCase):
    def setUp(self):
        seed(options.seed)

        from functools import partial
        self.poll = partial(poll, without_replacement=False)


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
        self.assertNotEqual(polling, Counter(vars(population)))
        self.assertEqual(polling.keys(), vars(population).keys())



class Test_Poll_Without_Replacement(unittest.TestCase):
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
        self.assertEqual(polling, Counter(vars(population)))



class Test_Variance(unittest.TestCase):
    def test_simple(self):
        args_result = {
            (0.0,) : 0.0,
            (0.1,) : 0.30000000000000004,
            (0.3,) : 0.458257569495584,
            (0.5,) : 0.5,
            (1.0,) : 0.0,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args), result)


    def test_multiple(self):
        args_result = {
            (0.0, 1)   : 0.0,
            (0.1, 3)   : 0.17320508075688773,
            (0.3, 20)  : 0.10246950765959598,
            (0.5, 90)  : 0.05270462766947299,
            (1.0, 999) : 0.0,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args), result)


    def test_fpc(self):
        args_result = {
            (0.0, 1, 20)   : 0.0,
            (0.1, 3, 20)   : 0.16383560438182507,
            (0.3, 20, 20)  : 0.0,
            (0.5, 90, 100)  : 0.0167506302543202,
            (1.0, 999, 1000) : 0.0,
        }

        for args, result in args_result.items():
            self.assertEqual(sigma(*args), result)



tests = [
    Test_Population,
    Test_Voting,
    Test_Tallying,
    Test_Poll_With_Replacement,
    Test_Poll_Without_Replacement,
    Test_Variance,
]
tests = [tests[t-1] for t in options.test]

runner = unittest.TextTestRunner()

for test in tests:
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(test)
    result = runner.run(test_suite)
